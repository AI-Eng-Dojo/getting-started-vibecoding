// Runs inside VS Code's embedded extension host, without npm or an external Node.
// API: https://code.visualstudio.com/api/working-with-extensions/testing-extension
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const vscode = require('vscode');

const evidenceDirectory = process.env.WINDOWS_EXTENSION_EVIDENCE;
const resultFile = path.join(evidenceDirectory, 'extension-result.json');
const result = { success: false, startedAt: new Date().toISOString() };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const writeJson = (name, value) => fs.writeFileSync(
  path.join(evidenceDirectory, name), JSON.stringify(value, null, 2),
);

exports.run = async () => {
  try {
    assert.equal(process.platform, 'win32');
    result.host = {
      vscode: vscode.version,
      executable: process.execPath,
      embeddedNodeVersion: process.versions.node,
      path: process.env.PATH,
    };
    assert.equal(vscode.version, '1.136.1');
    assert.equal(path.basename(process.execPath).toLowerCase(), 'code.exe');

    result.pathLookups = {};
    for (const command of ['node', 'npm', 'npx']) {
      const found = spawnSync(
        path.join(process.env.SystemRoot, 'System32', 'where.exe'), [command],
        { encoding: 'utf8', timeout: 10_000, windowsHide: true },
      );
      if (found.error) throw found.error;
      result.pathLookups[command] = {
        exitCode: found.status, stdout: found.stdout.trim(), stderr: found.stderr.trim(),
      };
      assert.equal(found.status, 1, `${command} must not resolve through PATH`);
      assert.equal(found.stdout.trim(), '');
    }

    const extension = vscode.extensions.getExtension('Anthropic.claude-code');
    assert.ok(extension, 'The unmodified Claude Code VSIX must be loaded');
    assert.equal(extension.packageJSON.version, '2.1.263');
    const processWrapper = vscode.workspace.getConfiguration('claudeCode').get('claudeProcessWrapper');
    assert.ok(processWrapper === undefined || processWrapper === '', 'No Claude process wrapper may be configured');
    result.extension = {
      id: extension.id, version: extension.packageJSON.version,
      path: extension.extensionPath, activeBeforeTest: extension.isActive,
    };
    await extension.activate();
    assert.equal(extension.isActive, true);
    result.activationSucceededAt = new Date().toISOString();

    await vscode.commands.executeCommand('claude-vscode.editor.open');
    const deadline = Date.now() + 20_000;
    let panel;
    do {
      panel = vscode.window.tabGroups.all.flatMap((group) => group.tabs).find(
        (tab) => tab.input instanceof vscode.TabInputWebview
          && tab.input.viewType.includes('claudeVSCodePanel'),
      );
      if (!panel) await sleep(100);
    } while (!panel && Date.now() < deadline);
    assert.ok(panel, 'Opening Claude Code must create its webview panel');
    result.panel = { label: panel.label, viewType: panel.input.viewType };

    const executable = path.join(extension.extensionPath, 'resources', 'native-binary', 'claude.exe');
    const cli = spawnSync(executable, ['--version'], {
      encoding: 'utf8', timeout: 20_000, windowsHide: true,
    });
    if (cli.error) throw cli.error;
    result.bundledCli = {
      executable, exitCode: cli.status, stdout: cli.stdout.trim(), stderr: cli.stderr.trim(),
    };
    assert.equal(cli.status, 0, 'The bundled native CLI must start');
    assert.match(cli.stdout, /^2\.1\.263\b/);

    // Allow the unmodified webview to render, then let PowerShell capture it.
    // The screenshot must be reviewed; a tab alone does not prove login UI rendered.
    await sleep(10_000);
    writeJson('capture-request.json', { requestedAt: new Date().toISOString() });
    const captureFile = path.join(evidenceDirectory, 'capture-result.json');
    const captureDeadline = Date.now() + 20_000;
    while (!fs.existsSync(captureFile) && Date.now() < captureDeadline) await sleep(100);
    assert.ok(fs.existsSync(captureFile), 'The Windows screenshot must be captured');
    result.capture = JSON.parse(fs.readFileSync(captureFile, 'utf8'));
    assert.equal(result.capture.success, true, result.capture.error);
    result.success = true;
  } catch (error) {
    result.error = error.stack || String(error);
    throw error;
  } finally {
    result.finishedAt = new Date().toISOString();
    result.scope = 'Unauthenticated activation, webview creation, and bundled CLI --version only. No prompt or paid API request is sent.';
    fs.writeFileSync(resultFile, JSON.stringify(result, null, 2));
  }
};
