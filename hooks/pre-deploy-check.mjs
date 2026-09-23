// wrangler deploy の前に、コミットしていない変更が無いかを確かめる
import { spawnSync } from "node:child_process";

const root = process.env.CLAUDE_PROJECT_DIR ?? process.cwd();
const r = spawnSync("git", ["status", "--porcelain"], { cwd: root, encoding: "utf8" });
if (r.error || r.status !== 0) {
  process.stderr.write("git status を実行できなかったため、デプロイを止めました。\n");
  process.exit(2);
}
if (r.stdout.trim() !== "") {
  process.stderr.write(
    "コミットしていない変更があるため、デプロイを止めました。\n" +
    r.stdout +
    "先にコミットして、コミット前のレビューを通してください。\n",
  );
  process.exit(2);
}
