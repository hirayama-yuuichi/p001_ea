# infra/windows フォルダ再構築

## やったこと
- `work.txt` の要望に基づき `infra/windows/` を再構築
- 既存機能の洗い出しとギャップ分析を実施

## 既存機能（変更前）
| フォルダ | 内容 |
|---|---|
| `autoshutdown/` | Windows内部タスクスケジューラで4時間後停止（**要件と不一致**） |
| `setup/` | Gitクローン + .venv + requirements インストール（継続） |

## 追加・変更した機能
| フォルダ | 内容 |
|---|---|
| `claude.md` | フォルダ専用ルール（設計方針・SSMパラメータ名など） |
| `autoshutdown/lambda_auto_stop.py` | Lambda + EventBridge による EC2 外部停止 |
| `startup/record_ip.ps1` | 起動時パブリックIP → SSM Parameter Store 記録 |
| `ebs_backup/lambda_ebs_backup.py` | 停止時 EBSスナップショット → EBS削除 |
| `mt5/README.md` | MT5機能の整理・Ubuntu連携方法 |

## 結果
- EC2外部シャットダウン・EBS退避・IP記録の仕組みをコードとして整備
- GitHub に push 済み

## 次のアクション
- Lambda 関数を実際に AWS にデプロイする
- IAM ロール（`p001ea-lambda-role`）を作成し必要な権限を付与
- EventBridge ルールを設定する
- `startup/record_ip.ps1` を Windows スタートアップタスクに登録する
