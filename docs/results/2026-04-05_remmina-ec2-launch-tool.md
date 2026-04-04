# EC2起動 + Remmina IP自動更新ツール作成

日付: 2026-04-05

## やったこと

- `infra/start-ec2-and-rdp.sh` を新規作成
- EC2 起動 → IP 取得 → Remmina プロファイル自動更新 → Remmina 起動 を一連で実行するスクリプト

### スクリプトの動作フロー

1. AWS SSO 認証済みプロファイルで EC2 を起動
2. `instance-running` になるまで待機
3. パブリック IP を取得
4. Remmina プロファイル（`ea` / `ea hy` 両方）の `server=` を新 IP に書き換え
5. ファイル名に含まれる IP 部分もダッシュ区切りでリネーム
6. `remmina` をプロファイル選択なしで起動（ユーザーが画面から選ぶ）

### 対象プロファイル（パターンで動的検索）

- `group_rdp_ea-hy_*.remmina`
- `group_rdp_ea_*.remmina`

## 結果

- 初回実行でエラー発生：ファイル名の IP をハードコードしていたため、前回リネーム済みファイルが見つからず `UPDATED_PROFILE` が空になり `remmina -c ""` が失敗
- 修正1：プロファイルをグロブパターンで動的検索に変更
- 修正2：ファイル名の IP はドット→ダッシュ変換して sed するよう修正
- 修正3：Remmina 起動をプロファイル指定なし（`remmina &`）に変更

## 使い方

```bash
# SSO トークン切れの場合は事前に実行
aws sso login --profile AdministratorAccess-042608219431

# EC2 起動 + Remmina 表示
bash /home/hy/workspace/p001_ea/infra/start-ec2-and-rdp.sh
```

## 次のアクション

- EC2 停止スクリプトも同様に整備するか検討
- 4時間自動シャットダウンの確認
