# GitHub SSH 運用ガイド（macOS） / GitHub SSH Operations Guide (macOS)

このドキュメントは、macOS から GitHub リポジトリを操作するための、**クリーンで監査可能（auditable）な SSH ベースのワークフロー**をまとめたものです。Github運用環境構築の際の覚え書きですが､公開ポートフォリオ用リポジトリに置くことを想定した、運用手順書（operational runbook）として書いています。

---

## 対象範囲（Scope）

- GitHub アクセス用の SSH 鍵ペア（keypair）の生成と管理
- OpenSSH クライアントの `~/.ssh/config` による設定
- 認証の検証と、よくある失敗の診断
- Git の remote を HTTPS ↔ SSH で切り替える
- 複数鍵（例: personal/work）を「後から破綻なく」運用拡張する

---

## 基本: GitHub を単一鍵で利用する（Baseline: single-key GitHub access）

### 1) `~/.ssh` を作成し、厳格な権限を設定する（Create `~/.ssh` and apply strict permissions）

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh

touch ~/.ssh/config
chmod 600 ~/.ssh/config
```

確認:

```bash
ls -ld ~/.ssh
ls -l ~/.ssh/config
```

---

### 2) Ed25519 鍵ペアを生成する（Generate an Ed25519 keypair）

例（鍵を `~/.ssh/github_ed25519` に保存する場合）:

```bash
ssh-keygen -t ed25519 -C "github" -f ~/.ssh/github_ed25519
chmod 600 ~/.ssh/github_ed25519
chmod 644 ~/.ssh/github_ed25519.pub
```

メモ:

- 非対話環境（non-interactive environment）で絶対に必要、などの事情がない限り、秘密鍵には passphrase を設定。
- `-C` は公開鍵の中に入る comment/label を設定するだけで、認証には使用されない。

---

### 3) `ssh-agent` を起動して鍵をロードする（macOS Keychain integration）

```bash
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/github_ed25519
ssh-add -l
```

期待される状態:

- `ssh-add` が “Identity added …” の行を出力する
- `ssh-add -l` でロード済みの鍵が一覧表示される

もし `--apple-use-keychain` が環境で未対応なら、付けずにロード:

```bash
ssh-add ~/.ssh/github_ed25519
```

---

### 4) GitHub 用に OpenSSH を設定する（Configure OpenSSH for GitHub）

次のブロックを `~/.ssh/config` に追記:

```sshconfig
Host github.com
  HostName github.com
  User git
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/github_ed25519
  IdentitiesOnly yes
```

意図（Rationale）:

- `IdentityFile` により「使う秘密鍵」を明示的に固定。
- `IdentitiesOnly yes` により、agent にロードされている無関係な鍵を SSH が提示しないようにする（認証失敗のノイズが減り、原因切り分けが容易になる）。

もし `UseKeychain` により `Bad configuration option` が出る場合、ファイルの先頭付近に次の行を追加する:

```sshconfig
IgnoreUnknown UseKeychain
```

---

### 5) 公開鍵を GitHub アカウントに登録する（Add the public key to your GitHub account）

公開鍵をクリップボードへコピー:

```bash
pbcopy < ~/.ssh/github_ed25519.pub
```

GitHub 側で登録:

- Settings → **SSH and GPG keys** → **New SSH key** → paste

---

### 6) GitHub への SSH 認証を検証する（Validate SSH authentication to GitHub）

```bash
ssh -T git@github.com
```

期待される挙動:

- 認証に成功し、GitHub が “shell access is not provided” を含むメッセージを返す（= 接続はできるが、シェルログインは提供しない）。

診断用（verbose）:

```bash
ssh -vT git@github.com
```

---

## SSH 経由の Git remotes（Git remotes over SSH）

### 既存リポジトリの remote を HTTPS から SSH に切り替える（Switch an existing repository from HTTPS to SSH）

既存 remote の確認:

```bash
git remote -v
```

SSH URL に変更:

```bash
git remote set-url origin git@github.com:OWNER/REPOSITORY.git
git remote -v
```

新しいローカルブランチで初回 push（tracking 設定を含む）:

```bash
git push -u origin main
```

---

## 拡張: 2つの鍵を使い分ける（personal/work）（Extension: dual-key operation）

追加の GitHub アカウントや、セキュリティ境界（security boundary）を分けたい場合は、2本目の鍵を作って `Host` の **alias（別名）**で経路分岐させる。これにより、後からの拡張でも設定を崩しにくくすることが可能。

### 1) 追加の鍵を作成する（Create additional keys）

```bash
ssh-keygen -t ed25519 -C "github-personal" -f ~/.ssh/github_personal_ed25519
ssh-keygen -t ed25519 -C "github-work"     -f ~/.ssh/github_work_ed25519

chmod 600 ~/.ssh/github_personal_ed25519 ~/.ssh/github_work_ed25519
chmod 644 ~/.ssh/github_personal_ed25519.pub ~/.ssh/github_work_ed25519.pub
```

両方を agent にロード:

```bash
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/github_personal_ed25519
ssh-add --apple-use-keychain ~/.ssh/github_work_ed25519
ssh-add -l
```

それぞれの公開鍵を、意図した GitHub アカウント側に登録する。

### 2) `~/.ssh/config` に host alias を設定する（Configure `~/.ssh/config` with host aliases）

```sshconfig
Host github-personal
  HostName github.com
  User git
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/github_personal_ed25519
  IdentitiesOnly yes

Host github-work
  HostName github.com
  User git
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/github_work_ed25519
  IdentitiesOnly yes
```

明示的にテスト:

```bash
ssh -T github-personal
ssh -T github-work
```

### 3) Git remote で alias を使う（Use the alias in Git remotes）

Personal:

```bash
git remote set-url origin git@github-personal:OWNER/REPOSITORY.git
```

Work（org/repo）:

```bash
git remote set-url origin git@github-work:ORG/REPOSITORY.git
```

remote URL の中で鍵選択が明示されるため、監査（audit）やインシデント対応（incident response）の際の曖昧さを減らせる。

---

## 鍵のローテーションと失効（Key rotation and revocation）

標準的な手順:

1. 新しい鍵ペアを生成する
2. 新しい公開鍵を GitHub に登録する
3. `~/.ssh/config` の `IdentityFile`（または alias ブロック）を更新する
4. `ssh -T …` で検証する
5. GitHub のアカウント設定から古い鍵を削除する
6. 必要なら agent から古い鍵を除去する:

```bash
ssh-add -D
# then re-add only the required keys
```

---

## トラブルシューティング（Troubleshooting checklist）

### `Permission denied (publickey).`

- 公開鍵が GitHub に登録されていることを確認する
- 意図した鍵がロードされていることを確認する:

```bash
ssh-add -l
```

- `IdentityFile` と `IdentitiesOnly` が意図通り効いているか確認する:

```bash
ssh -G github.com | grep -E 'identityfile|identitiesonly|user'
```

- verbose で認証を追う:

```bash
ssh -vT git@github.com
```

### `Bad owner or permissions on ~/.ssh/...`

厳格な権限を再適用:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/github_ed25519
chmod 644 ~/.ssh/github_ed25519.pub
```

### `Too many authentication failures`

- `IdentitiesOnly yes` が設定されていることを確認する
- 対象の `Host` ブロックで `IdentityFile` により鍵を固定する

### Host key warnings（例: “Host key verification failed”）

- host key のプロンプトを盲目的に無視しない
- セキュリティポリシー（security posture）に応じて host key を検証し、必要に応じて `~/.ssh/known_hosts` を更新する

---

## 参考資料（一次情報）（References (primary sources)）

### GitHub Docs (SSH)

- [Connecting to GitHub with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [Generating a new SSH key and adding it to the ssh-agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
- [Managing remote repositories](https://docs.github.com/en/get-started/git-basics/managing-remote-repositories)
- [Error: ssh-add: illegal option -- -apple-use-keychain](https://docs.github.com/en/authentication/troubleshooting-ssh/error-ssh-add-illegal-option----apple-use-keychain)

### OpenSSH documentation

- [ssh_config(5)](https://man.openbsd.org/ssh_config)
