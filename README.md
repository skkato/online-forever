# Online Forever — Render用

Discordアカウントを24/7オンラインに保つスクリプト（SealedSaucer/Online-Forever）を
Render無料枠で動かせるようにしたもの。

## デプロイ手順

1. このフォルダの中身をGitHubの新規リポジトリにアップロード
2. Renderに登録 → New + → Web Service → そのリポジトリを選択
   （render.yamlがあるので設定は自動で入る。プランはFreeを選ぶ）
3. Environment（環境変数）に `DISCORD_TOKEN` = 自分のDiscordトークンを入れる
   - `DISCORD_STATUS`: online / dnd / idle から変更可
   - `CUSTOM_STATUS`: カスタムステータスの文言（空にすると表示なし）
4. デプロイ完了後、表示されるURL（https://online-forever-xxxx.onrender.com）を
   UptimeRobotに登録し、5分間隔のHTTPモニターを追加する
   （Render無料枠は15分アクセスがないと寝るため）

## 注意

- トークンはパスワードと同等。コードに直接書かず、必ず環境変数で入れること
- ユーザーアカウントの自動化はDiscordの利用規約違反で、アカウント停止の可能性がある
- Render無料枠は月750時間まで。サービスは1個だけにすること
