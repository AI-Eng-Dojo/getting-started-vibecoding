// /code-review を打ったときに、コードレビューの制御ファイルを更新する
import { writeFileSync } from "node:fs";
import { join } from "node:path";

const root = process.env.CLAUDE_PROJECT_DIR ?? process.cwd();
writeFileSync(join(root, ".claude", "code-reviewed"), new Date().toISOString() + "\n");
