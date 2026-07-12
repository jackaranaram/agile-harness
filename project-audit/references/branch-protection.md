# Branch Protection Fix

Configures branch protection on the default branch via GitHub API.

## Prerequisites

- `gh` CLI authenticated (`gh auth status`)
- User must have admin permissions on the repo

## Default Payload

Recommended protection rules for professional projects:

```json
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
```

## Execution

```powershell
$owner = "extract from git remote"
$repo = "extract from git remote"
$default = "main" # or master

# Build JSON payload
$json = @'
{payload above}
'@

# Write to temp file and apply
$tempFile = [System.IO.Path]::GetTempFileName()
Set-Content -Path $tempFile -Value $json
gh api repos/$owner/$repo/branches/$default/protection --method PUT --input $tempFile
Remove-Item -Path $tempFile
```

## Verify

```powershell
gh api repos/$owner/$repo/branches/$default/protection | ConvertFrom-Json
```

Look for `enabled: true` on:

- `required_pull_request_reviews`
- `enforce_admins`
- `required_linear_history`
- `allow_force_pushes.enabled: false`
- `allow_deletions.enabled: false`
