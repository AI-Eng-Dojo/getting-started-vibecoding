import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import {
  existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, statSync, utimesSync, writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const hooks = dirname(fileURLToPath(import.meta.url));
const oldTime = new Date("2020-01-01T00:00:00Z");
const reviewedTime = new Date("2020-01-02T00:00:00Z");
const editedTime = new Date("2020-01-03T00:00:00Z");

function git(root, ...args) {
  const result = spawnSync("git", [
    "-c", "core.hooksPath=" + join(root, "disabled-hooks"),
    "-c", "commit.gpgsign=false",
    "-c", "user.name=Hook Test", "-c", "user.email=hook-test@example.invalid",
    ...args,
  ], { cwd: root, encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout;
}

function fixture(t, { repository = true } = {}) {
  // A path with spaces checks the same argv-based invocation used by settings.json.
  const root = mkdtempSync(join(tmpdir(), "vibecoding hook test "));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  mkdirSync(join(root, ".claude"));
  if (repository) {
    git(root, "init", "--quiet");
    writeFileSync(join(root, ".gitignore"), ".claude/code-reviewed\nignored/\n");
    writeFileSync(join(root, "app.js"), "console.log('fixture');\n");
    writeFileSync(join(root, "README.md"), "# Fixture\n");
    git(root, "add", ".gitignore", "app.js", "README.md");
    git(root, "commit", "--quiet", "-m", "fixture");
    for (const file of [".gitignore", "app.js", "README.md"]) {
      utimesSync(join(root, file), oldTime, oldTime);
    }
  }
  return root;
}

function mark(root, time = reviewedTime) {
  const marker = join(root, ".claude", "code-reviewed");
  writeFileSync(marker, "review started\n");
  utimesSync(marker, time, time);
  return marker;
}

function run(root, name, { cwd = root, env = {} } = {}) {
  return spawnSync(process.execPath, [join(hooks, name)], {
    cwd, encoding: "utf8", env: { ...process.env, CLAUDE_PROJECT_DIR: root, ...env },
  });
}

function assertDenied(result, reason) {
  assert.equal(result.status, 0, result.stderr);
  const output = JSON.parse(result.stdout).hookSpecificOutput;
  assert.equal(output.hookEventName, "PreToolUse");
  assert.equal(output.permissionDecision, "deny");
  assert.match(output.permissionDecisionReason, reason);
  assert.equal(output.additionalContext, output.permissionDecisionReason);
}

function assertAllowed(result) {
  assert.equal(result.status, 0, result.stderr);
  assert.equal(result.stdout, "");
  assert.equal(result.stderr, "");
}

test("code review pauses once and permits an unchanged retry before any review result", (t) => {
  const root = fixture(t);
  assertDenied(run(root, "pre-commit-code-review.mjs"), /\/code-review/);
  assert.ok(existsSync(join(root, ".claude", "code-reviewed")));
  assertAllowed(run(root, "pre-commit-code-review.mjs"));
});

test("newer file timestamps trigger review even when the Git contents did not change", (t) => {
  const root = fixture(t);
  mark(root);
  assertAllowed(run(root, "pre-commit-code-review.mjs"));
  utimesSync(join(root, "app.js"), editedTime, editedTime);
  assert.equal(git(root, "status", "--porcelain"), "");
  assertDenied(run(root, "pre-commit-code-review.mjs"), /変更したファイル/);
});

test("manual review invocation refreshes the start marker using the project root", (t) => {
  const root = fixture(t);
  const marker = mark(root);
  const previous = statSync(marker).mtimeMs;
  utimesSync(join(root, "app.js"), editedTime, editedTime);
  assertAllowed(run(root, "mark-code-reviewed.mjs", { cwd: tmpdir() }));
  assert.ok(statSync(marker).mtimeMs > previous);
  assert.ok(Number.isFinite(Date.parse(readFileSync(marker, "utf8").trim())));
  assertAllowed(run(root, "pre-commit-code-review.mjs", { cwd: tmpdir() }));
});

test("Markdown changes, including uppercase extensions and new files, do not pause code review", (t) => {
  const root = fixture(t);
  mark(root);
  writeFileSync(join(root, "README.md"), "# Changed\n");
  writeFileSync(join(root, "TASKS.MD"), "# New\n");
  git(root, "add", "README.md");
  assertAllowed(run(root, "pre-commit-code-review.mjs"));
});

test("deletion alone does not pause code review", (t) => {
  const root = fixture(t);
  mark(root);
  rmSync(join(root, "app.js"));
  assertAllowed(run(root, "pre-commit-code-review.mjs"));
  git(root, "add", "app.js");
  assertAllowed(run(root, "pre-commit-code-review.mjs"));
});

test("new non-Markdown files pause review while ignored files do not", (t) => {
  const root = fixture(t);
  mark(root);
  mkdirSync(join(root, "ignored"));
  writeFileSync(join(root, "ignored", "cache.js"), "cached\n");
  assertAllowed(run(root, "pre-commit-code-review.mjs"));
  writeFileSync(join(root, "new app.js"), "console.log('new');\n");
  assertDenied(run(root, "pre-commit-code-review.mjs"), /変更したファイル/);
});

test("code review denies when Git cannot inspect the repository", (t) => {
  const root = fixture(t, { repository: false });
  assertDenied(run(root, "pre-commit-code-review.mjs"), /git ls-files/);
  assert.equal(existsSync(join(root, ".claude", "code-reviewed")), false);
});

test("deployment permits a clean repository and ignores the review marker", (t) => {
  const root = fixture(t);
  mark(root);
  assertAllowed(run(root, "pre-deploy-check.mjs", { cwd: tmpdir() }));
});

test("deployment rejects unstaged changes, staged changes, and untracked files", async (t) => {
  for (const state of ["unstaged", "staged", "untracked"]) {
    await t.test(state, (subtest) => {
      const root = fixture(subtest);
      const file = state === "untracked" ? "new app.js" : "app.js";
      writeFileSync(join(root, file), "console.log('changed');\n");
      if (state === "staged") git(root, "add", file);
      const result = run(root, "pre-deploy-check.mjs");
      assert.equal(result.status, 2);
      assert.match(result.stderr, /コミットしていない変更/);
      assert.ok(result.stderr.includes(file));
      assert.equal(result.stdout, "");
    });
  }
});

test("deployment rejects deletion but excludes ignored files", (t) => {
  const root = fixture(t);
  mkdirSync(join(root, "ignored"));
  writeFileSync(join(root, "ignored", "cache.js"), "cached\n");
  assertAllowed(run(root, "pre-deploy-check.mjs"));
  rmSync(join(root, "app.js"));
  assert.equal(run(root, "pre-deploy-check.mjs").status, 2);
});

test("deployment stops when Git cannot inspect the repository or cannot be launched", (t) => {
  const root = fixture(t, { repository: false });
  for (const env of [{}, { PATH: root }]) {
    const result = run(root, "pre-deploy-check.mjs", { env });
    assert.equal(result.status, 2);
    assert.match(result.stderr, /git status を実行できなかった/);
  }
});
