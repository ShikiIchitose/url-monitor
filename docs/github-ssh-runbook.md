# GitHub SSH Operations Guide (macOS)

This document describes a clean, auditable SSH-based workflow for operating GitHub repositories from macOS. It is written as an operational runbook suitable for a public portfolio repository.

---

## Scope

- Generate and manage SSH keypairs for GitHub access
- Configure the OpenSSH client via `~/.ssh/config`
- Validate authentication and diagnose common failures
- Switch Git remotes between HTTPS and SSH
- Extend the configuration to multiple keys (e.g., personal/work) without rework

---

## Baseline: single-key GitHub access

### 1) Create `~/.ssh` and apply strict permissions

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh

touch ~/.ssh/config
chmod 600 ~/.ssh/config
```

Verify:

```bash
ls -ld ~/.ssh
ls -l ~/.ssh/config
```

---

### 2) Generate an Ed25519 keypair

Example (key stored as `~/.ssh/github_ed25519`):

```bash
ssh-keygen -t ed25519 -C "github" -f ~/.ssh/github_ed25519
chmod 600 ~/.ssh/github_ed25519
chmod 644 ~/.ssh/github_ed25519.pub
```

Notes:

- Use a passphrase for the private key unless a non-interactive environment strictly requires otherwise.
- `-C` sets a comment/label inside the public key; it is not used for authentication.

---

### 3) Start `ssh-agent` and load the key (macOS Keychain integration)

```bash
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/github_ed25519
ssh-add -l
```

Expected outcome:

- `ssh-add` prints an “Identity added …” line.
- `ssh-add -l` lists the loaded key.

If `--apple-use-keychain` is unsupported in your environment, load without it:

```bash
ssh-add ~/.ssh/github_ed25519
```

---

### 4) Configure OpenSSH for GitHub

Append the following block to `~/.ssh/config`:

```sshconfig
Host github.com
  HostName github.com
  User git
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/github_ed25519
  IdentitiesOnly yes
```

Rationale:

- `IdentityFile` pins the exact private key to use.
- `IdentitiesOnly yes` prevents SSH from offering unrelated keys from the agent (reduces auth failure noise).

If `UseKeychain` causes `Bad configuration option`, add this line near the top of the file:

```sshconfig
IgnoreUnknown UseKeychain
```

---

### 5) Add the public key to your GitHub account

Copy the public key to clipboard:

```bash
pbcopy < ~/.ssh/github_ed25519.pub
```

Then add it in GitHub:

- Settings → **SSH and GPG keys** → **New SSH key** → paste

---

### 6) Validate SSH authentication to GitHub

```bash
ssh -T git@github.com
```

Expected behavior:

- Authentication succeeds and GitHub returns a message indicating that shell access is not provided.

Diagnostic mode (verbose):

```bash
ssh -vT git@github.com
```

---

## Git remotes over SSH

### Switch an existing repository from HTTPS to SSH

List existing remotes:

```bash
git remote -v
```

Set SSH URL:

```bash
git remote set-url origin git@github.com:OWNER/REPOSITORY.git
git remote -v
```

First push from a new local branch tracking configuration:

```bash
git push -u origin main
```

---

## Extension: dual-key operation (personal/work)

When an additional GitHub account or distinct security boundary is required, add a second key and route selection through host aliases.

### 1) Create additional keys

```bash
ssh-keygen -t ed25519 -C "github-personal" -f ~/.ssh/github_personal_ed25519
ssh-keygen -t ed25519 -C "github-work"     -f ~/.ssh/github_work_ed25519

chmod 600 ~/.ssh/github_personal_ed25519 ~/.ssh/github_work_ed25519
chmod 644 ~/.ssh/github_personal_ed25519.pub ~/.ssh/github_work_ed25519.pub
```

Load both into the agent:

```bash
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/github_personal_ed25519
ssh-add --apple-use-keychain ~/.ssh/github_work_ed25519
ssh-add -l
```

Register each corresponding public key in the intended GitHub account.

### 2) Configure `~/.ssh/config` with host aliases

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

Test explicitly:

```bash
ssh -T github-personal
ssh -T github-work
```

### 3) Use the alias in Git remotes

Personal:

```bash
git remote set-url origin git@github-personal:OWNER/REPOSITORY.git
```

Work (org/repo):

```bash
git remote set-url origin git@github-work:ORG/REPOSITORY.git
```

This makes key selection explicit in the remote URL, reducing ambiguity during audits and incident response.

---

## Key rotation and revocation

Standard approach:

1. Generate a new keypair.
2. Register the new public key in GitHub.
3. Update `IdentityFile` (or the alias block) in `~/.ssh/config`.
4. Validate with `ssh -T …`.
5. Remove the old key from GitHub account settings.
6. Remove old keys from the agent if needed:

```bash
ssh-add -D
# then re-add only the required keys
```

---

## Troubleshooting checklist

### `Permission denied (publickey).`

- Confirm the public key is registered in GitHub.
- Confirm the intended key is loaded:

```bash
ssh-add -l
```

- Confirm `IdentityFile` and `IdentitiesOnly` are effective:

```bash
ssh -G github.com | grep -E 'identityfile|identitiesonly|user'
```

- Run verbose authentication:

```bash
ssh -vT git@github.com
```

### `Bad owner or permissions on ~/.ssh/...`

Apply strict permissions:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/github_ed25519
chmod 644 ~/.ssh/github_ed25519.pub
```

### `Too many authentication failures`

- Ensure `IdentitiesOnly yes` is set.
- Pin the key via `IdentityFile` for the relevant `Host` block.

### Host key warnings (e.g., “Host key verification failed”)

- Do not ignore host key prompts blindly.
- Validate the host key and update `~/.ssh/known_hosts` as appropriate for your security posture.

---

## References (primary sources)

GitHub Docs (SSH):

```text
https://docs.github.com/en/authentication/connecting-to-github-with-ssh
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
https://docs.github.com/en/get-started/git-basics/managing-remote-repositories
https://docs.github.com/en/authentication/troubleshooting-ssh/error-ssh-add-illegal-option----apple-use-keychain
```

OpenSSH documentation:

```text
https://man.openbsd.org/ssh_config
```
