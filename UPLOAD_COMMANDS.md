# Quick Commands to Upload to GitHub

## Step 1: Create Repository on GitHub
1. Go to https://github.com/new
2. Repository name: `Open-JDK-Upgrade-Agent`
3. Description: `Cross-platform Python agent to automate OpenJDK detection, backup, and upgrade`
4. Choose Public or Private
5. **DO NOT** check any initialization options
6. Click "Create repository"

## Step 2: Copy Your GitHub Username
After creating the repo, note your GitHub username from the URL:
`https://github.com/YOUR-USERNAME/Open-JDK-Upgrade-Agent`

## Step 3: Run These Commands

Open PowerShell in this directory and run:

```powershell
# Replace YOUR-USERNAME with your actual GitHub username
git remote add origin https://github.com/YOUR-USERNAME/Open-JDK-Upgrade-Agent.git

# Rename branch to main (GitHub's default)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 4: Enter Credentials
When prompted:
- **Username**: Your GitHub username
- **Password**: Your Personal Access Token (NOT your GitHub password)

### Don't have a token? Create one:
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: `OpenJDK Agent Upload`
4. Select scope: `repo` (full control of private repositories)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

## That's It! 🎉

Your repository will be live at:
`https://github.com/YOUR-USERNAME/Open-JDK-Upgrade-Agent`

## Quick Verification

```powershell
# Check remote is set correctly
git remote -v

# View commit history
git log --oneline

# Check status
git status
```

## Next Steps (Optional)

1. **Add topics** on GitHub to help discovery
2. **Create a release** (v1.0.0)
3. **Enable Issues** for bug reports
4. **Share your project!**

---

**Need detailed help?** See `GITHUB_UPLOAD_GUIDE.md` for comprehensive instructions.
