// git commit の前に、コードレビューのあとに変更したファイルがあれば、コミットをいったん止める
import { spawnSync } from "node:child_process";
import { existsSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const root = process.env.CLAUDE_PROJECT_DIR ?? process.cwd();
const marker = join(root, ".claude", "code-reviewed");
const docFile = /\.md$/i; // Markdownの文書は、判定から外す

// コミットを止め、理由をClaudeに伝える
function deny(message) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: message,
      additionalContext: message, // ほかのフックも止めたときに、この理由が届かなくならないようにする
    },
  }));
  process.exit(0);
}

const r = spawnSync("git", ["ls-files", "--cached", "--others", "--exclude-standard", "-z"], {
  cwd: root, encoding: "utf8",
});
if (r.error || r.status !== 0) {
  deny("git ls-files を実行できなかったため、コミットを止めました。");
}
const files = r.stdout.split("\0").filter((f) => f && !docFile.test(f) && existsSync(join(root, f)));
const newest = Math.max(0, ...files.map((f) => statSync(join(root, f)).mtimeMs));
const reviewedAt = existsSync(marker) ? statSync(marker).mtimeMs : 0;

if (newest > reviewedAt) {
  // 止めるのは一度だけ。次に同じコミットを試したときは通す
  writeFileSync(marker, new Date().toISOString() + "\n");
  deny(
    "前回のコードレビューのあとに変更したファイルがあるため、コミットをいったん止めました。\n" +
    "/code-review を実行し、指摘をユーザーに報告して、直すか、このままコミットするかを確認してください。\n" +
    "このままコミットする場合は、同じコミットをもう一度実行してください。",
  );
}
