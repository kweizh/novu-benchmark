import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/app"

def test_dynamic_provider_implementation():
    """Priority 1: Use a custom Node.js script to execute the workflow and verify the provider overrides."""
    
    test_script_path = "/tmp/verify_workflow.js"
    test_script_content = """
const http = require('http');
const { dynamicProvider } = require('/home/user/app/app/api/novu/workflows.ts');

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname === '/config') {
    const userId = url.searchParams.get('userId');
    res.writeHead(200, { 'Content-Type': 'application/json' });
    if (userId === 'user_sendgrid') {
      res.end(JSON.stringify({ provider: 'sendgrid', templateId: 'sg-123', data: { role: 'admin' } }));
    } else if (userId === 'user_mailgun') {
      res.end(JSON.stringify({ provider: 'mailgun', templateId: 'mg-456', data: { role: 'user' } }));
    } else {
      res.end(JSON.stringify({ provider: 'none', templateId: '', data: {} }));
    }
  } else {
    res.writeHead(404);
    res.end();
  }
});

server.listen(4000, async () => {
  try {
    if (!dynamicProvider) {
      throw new Error("dynamicProvider workflow is not exported from workflows.ts");
    }

    const res = await dynamicProvider.discover();

    // Test 1: Sendgrid
    let sgCustomResult = null;
    let sgEmailResult = null;
    await res.execute({
      payload: { orderId: 'ord_111' },
      subscriber: { subscriberId: 'user_sendgrid' },
      step: {
        custom: async (id, resolver) => {
          sgCustomResult = await resolver();
          return sgCustomResult;
        },
        email: async (id, resolver) => {
          sgEmailResult = await resolver();
          return sgEmailResult;
        }
      }
    });

    if (!sgEmailResult || !sgEmailResult.providers || !sgEmailResult.providers.sendgrid) {
      throw new Error("Sendgrid provider override missing or incorrect.");
    }
    if (sgEmailResult.providers.sendgrid.templateId !== 'sg-123') {
      throw new Error("Sendgrid templateId is incorrect.");
    }
    if (sgEmailResult.providers.sendgrid.dynamicTemplateData.role !== 'admin') {
      throw new Error("Sendgrid dynamicTemplateData is incorrect.");
    }
    if (sgEmailResult.subject !== 'Order ord_111') {
      throw new Error("Email subject is incorrect for Sendgrid test.");
    }

    // Test 2: Mailgun
    let mgCustomResult = null;
    let mgEmailResult = null;
    await res.execute({
      payload: { orderId: 'ord_222' },
      subscriber: { subscriberId: 'user_mailgun' },
      step: {
        custom: async (id, resolver) => {
          mgCustomResult = await resolver();
          return mgCustomResult;
        },
        email: async (id, resolver) => {
          mgEmailResult = await resolver();
          return mgEmailResult;
        }
      }
    });

    if (!mgEmailResult || !mgEmailResult.providers || !mgEmailResult.providers.mailgun) {
      throw new Error("Mailgun provider override missing or incorrect.");
    }
    if (mgEmailResult.providers.mailgun.template !== 'mg-456') {
      throw new Error("Mailgun template is incorrect.");
    }
    if (mgEmailResult.providers.mailgun['h:X-Mailgun-Variables'] !== JSON.stringify({ role: 'user' })) {
      throw new Error("Mailgun h:X-Mailgun-Variables is incorrect.");
    }
    if (mgEmailResult.subject !== 'Order ord_222') {
      throw new Error("Email subject is incorrect for Mailgun test.");
    }

    // Test 3: None
    let noneCustomResult = null;
    let noneEmailResult = null;
    await res.execute({
      payload: { orderId: 'ord_333' },
      subscriber: { subscriberId: 'user_none' },
      step: {
        custom: async (id, resolver) => {
          noneCustomResult = await resolver();
          return noneCustomResult;
        },
        email: async (id, resolver) => {
          noneEmailResult = await resolver();
          return noneEmailResult;
        }
      }
    });

    if (noneEmailResult.providers && Object.keys(noneEmailResult.providers).length > 0) {
      throw new Error("Providers override should not be present when provider is 'none'.");
    }

    console.log("SUCCESS");
    process.exit(0);
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  } finally {
    server.close();
  }
});
"""
    with open(test_script_path, "w") as f:
        f.write(test_script_content)

    # Use tsx to run the script since workflows.ts is TypeScript
    result = subprocess.run(
        ["npx", "tsx", test_script_path],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR
    )

    assert result.returncode == 0, f"Workflow verification failed: {result.stderr.strip() or result.stdout.strip()}"
    assert "SUCCESS" in result.stdout, f"Workflow verification did not succeed: {result.stdout.strip()}"
