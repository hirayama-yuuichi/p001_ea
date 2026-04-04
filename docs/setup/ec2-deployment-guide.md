# EC2 CloudFormation デプロイガイド

## テンプレート概要

`infra/ec2-windows-mt5.yaml` は以下をワンステップで構築します：

- Windows Server 2022 インスタンス
- t3.medium（カスタマイズ可）
- 100GB EBS ボリューム
- セキュリティグループ（RDP + SSH 許可）
- IAM ロール（SSM Session Manager対応）
- 自動シャットダウン（起動後 4 時間）

---

## デプロイ手順

### 1. AWS Console にログイン
```
https://d-9567b23e2d.awsapps.com/start/#
```

### 2. CloudFormation に移動
- **AWS Console** → **CloudFormation** → **スタック作成**

### 3. テンプレートをアップロード
- **テンプレートの準備**
  - 「テンプレートファイルのアップロード」を選択
  - `ec2-windows-mt5.yaml` を選択

### 4. スタック詳細を入力
- **スタック名**: `p001-ea-ec2` （任意）
- **パラメータ**:
  - **InstanceType**: `t3.medium` （デフォルト、変更可）
  - **VolumeSize**: `100` （デフォルト）
  - **KeyName**: AWS で生成済みの KeyPair 名を選択
    - 未生成の場合：EC2 ダッシュボーム → **キーペア** → **キーペアを作成**

### 5. スタックオプション
- そのままで OK（変更不要）

### 6. レビュー → 作成
- **「スタックの作成」** をクリック
- 2～5 分で完了

---

## デプロイ完了後

### 出力情報を確認
CloudFormation コンソール → スタック → **出力** タブ

以下の情報が表示されます：

```
InstanceId:     i-xxxxxxxxxx
PublicIP:       54.xxx.xxx.xxx
RDPCommand:     mstsc /v:54.xxx.xxx.xxx
SSHCommand:     ssh -i your-key.pem Administrator@54.xxx.xxx.xxx
```

### RDP で接続
```bash
mstsc /v:<PublicIP>
```

### SSH で接続
```bash
ssh -i /path/to/your-key.pem Administrator@<PublicIP>
```

---

## トラブルシューティング

### キーペアが見つからない
1. EC2 ダッシュボーム → **キーペア** を確認
2. キーペアが無い場合、新規作成
3. CloudFormation の **KeyName** パラメータで指定

### インスタンスが起動しない
- CloudFormation スタック → **イベント** タブでエラーを確認
- IAM 権限が不足していないか確認

### RDP/SSH で接続できない
1. セキュリティグループが RDP(3389) / SSH(22) を許可しているか確認
2. インスタンスが `running` 状態か確認
3. キーペアが正しいか確認

---

## 環境構築後（EC2 内）

自動実行される内容：
- Chocolatey インストール
- Git インストール
- Python インストール
- OpenSSH サーバー 起動

手動でやること：
- [ ] MT5 ダウンロード・インストール
- [ ] Claude Code インストール（オプション）
- [ ] リポジトリをクローン
