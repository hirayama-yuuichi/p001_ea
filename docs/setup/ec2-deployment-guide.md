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

### RDP で接続（Remmina 使用 - Ubuntu）
```bash
# Remmina インストール
sudo apt-get install remmina -y

# Remmina で接続
remmina
```
- **サーバー**: `<PublicIP>`
- **ユーザー名**: `Administrator`
- **接続タイプ**: RDP

または **Ubuntu デスクトップ → リモートデスクトップアプリ** から接続

### SSH で接続（推奨 - Ubuntu）
```bash
# キーペアのパーミッション設定
chmod 400 /path/to/your-key.pem

# SSH 接続
ssh -i /path/to/your-key.pem Administrator@<PublicIP>
```

**例:**
```bash
ssh -i ~/Downloads/p001-ea-key.pem Administrator@54.123.45.67
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

## Ubuntu ローカルからの接続設定

### 事前準備
```bash
# キーペアをダウンロード後、パーミッション設定
chmod 400 ~/Downloads/p001-ea-key.pem

# SSH 接続用エイリアス設定（オプション）
echo 'alias ssh-ec2="ssh -i ~/Downloads/p001-ea-key.pem Administrator@<PublicIP>"' >> ~/.bashrc
source ~/.bashrc
```

### ファイル転送（Ubuntu ↔ EC2）
```bash
# EC2 に送信
scp -i ~/Downloads/p001-ea-key.pem /local/path/file.py Administrator@<PublicIP>:C:/Users/Administrator/Desktop/

# EC2 から受信
scp -i ~/Downloads/p001-ea-key.pem Administrator@<PublicIP>:C:/path/file.txt ~/Downloads/
```

---

## 環境構築後（EC2 内）

### 自動実行される内容
- Chocolatey インストール
- Git インストール
- Python インストール
- OpenSSH サーバー 起動

### 手動でやること
- [ ] MT5 ダウンロード・インストール（RDP で EC2 に接続）
- [ ] Claude Code インストール（オプション）
- [ ] リポジトリをクローン

```powershell
# EC2 内で実行
git clone https://github.com/hirayama-yuuichi/p001_ea.git
cd p001_ea
```
