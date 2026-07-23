# 開発用EC2(Windows/mt5) 起動・RDP接続手順

## やりたいこと

- 開発用EC2（Windows, インスタンス名: `mt5`）が停止していたら起動する
- 起動後、パブリックIPアドレスを取得する
- 取得したIPに対してリモートデスクトップ（remmina）で接続する

これらを1コマンドで行うスクリプトを用意した。

- スクリプト: [`start-and-connect-rdp.sh`](./start-and-connect-rdp.sh)
- 対象インスタンス: `i-06f228c7623eba3a7`（インスタンス名: `mt5`）
- プロファイル: `AdministratorAccess-042608219431`
- リージョン: `ap-northeast-1`

[`1000_開発EC2WIN停止仕様.md`](./1000_開発EC2WIN停止仕様.md) で作成した自動停止（毎日 JST 9,21,0時）と対になる、起動・接続用のスクリプトである。

## 前提

- AWS CLI v2 がインストールされていること
- IAM Identity Center へのアクセス権（プロファイル `AdministratorAccess-042608219431`）があること
- remmina がインストールされていること（Ubuntu の場合 `sudo apt install remmina remmina-plugin-rdp`）

## 使い方

```bash
cd "1000_mt5シュミレータ/開発用ec2"
./start-and-connect-rdp.sh
```

## スクリプトの処理内容

1. **SSOログイン状態を確認**
   - `aws sts get-caller-identity` が失敗する場合、`aws sso login --profile AdministratorAccess-042608219431` を自動実行する
2. **インスタンス状態を確認**
   - `stopped` の場合は `aws ec2 start-instances` で起動する
   - `running` の場合は何もせず次に進む
   - `pending`/`stopping`/`shutting-down` の場合は `running` になるまで待機する
3. **起動完了を待機**
   - `aws ec2 wait instance-running` で `running` になるまでポーリングする
4. **パブリックIPアドレスを取得**
   - 起動直後はIP付与に数秒〜数十秒かかるため、最大180秒（5秒間隔）でリトライする
   - サブネットは `MapPublicIpOnLaunch=true` のため、起動時に自動でパブリックIPが付与される
5. **リモートデスクトップで接続**
   - `remmina -c rdp://<パブリックIP>` を実行する
   - ユーザー名・パスワードはremminaのダイアログで入力する（本スクリプトは資格情報を扱わない）

## 注意事項

- パブリックIPはインスタンス再起動のたびに変わる（Elastic IPを割り当てていないため）
- セキュリティグループでRDP(3389番ポート)が自分の接続元IPに対して許可されている必要がある。許可されていない場合は事前にセキュリティグループを見直すこと
- 本スクリプトは起動・IP取得・接続のみを行う。停止は行わない（停止は [`1000_開発EC2WIN停止仕様.md`](./1000_開発EC2WIN停止仕様.md) の自動停止スケジュールに従う、または手動で `aws ec2 stop-instances` を実行する）
