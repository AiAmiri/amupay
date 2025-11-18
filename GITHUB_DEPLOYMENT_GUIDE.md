# Complete Guide: Push AMU Pay Project to GitHub

This guide will walk you through pushing your AMU Pay project to GitHub step by step.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Prepare Your Project](#prepare-your-project)
3. [Create GitHub Repository](#create-github-repository)
4. [Initialize Git Repository](#initialize-git-repository)
5. [Add Files to Git](#add-files-to-git)
6. [Create Initial Commit](#create-initial-commit)
7. [Connect to GitHub](#connect-to-github)
8. [Push to GitHub](#push-to-github)
9. [Verify Upload](#verify-upload)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Git installed** on your computer
- ✅ **GitHub account** created
- ✅ **GitHub Personal Access Token** (for authentication)
- ✅ **Project files** ready
- ✅ **PowerShell** (for Windows - comes pre-installed)

### Quick Start Option

**For Windows users, you can use the automated script:**

1. Open PowerShell in the project directory
2. Run: `.\push_to_github.ps1`
3. Follow the prompts

The script will handle most steps automatically!

### Check if Git is Installed

**Windows (PowerShell/CMD):**
```bash
git --version
```

**If Git is not installed:**
- Download from: https://git-scm.com/download/win
- Install with default settings
- Restart your terminal after installation

### Verify Git Installation

```bash
git --version
# Should show: git version 2.x.x or higher
```

---

## Prepare Your Project

### Step 1: Verify .gitignore File

Your project already has a `.gitignore` file that excludes:
- `.env` files (sensitive credentials)
- `venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `*.pem` and `*.key` (SSH keys)
- Media files and static files
- Log files

**Important:** Never commit `.env` files or credentials to GitHub!

### Step 2: Check for Sensitive Files

Before pushing, verify no sensitive files are in the project:

```bash
# Check if .env file exists (should be ignored by git)
dir .env
# or
ls -la .env

# Check for any .pem files
dir *.pem
```

**If you find sensitive files:**
- Ensure they're in `.gitignore`
- If already committed, remove them (see troubleshooting section)

### Step 3: Create .gitkeep Files (Optional)

If you want to keep empty directories in Git:

```bash
# For media directory
New-Item -ItemType File -Path "amu_pay\media\.gitkeep" -Force

# For staticfiles directory
New-Item -ItemType File -Path "amu_pay\staticfiles\.gitkeep" -Force
```

---

## Create GitHub Repository

### Step 1: Login to GitHub

1. Go to https://github.com
2. Sign in to your account (or create one if you don't have it)

### Step 2: Create New Repository

1. Click the **"+"** icon in the top right corner
2. Select **"New repository"**

### Step 3: Configure Repository

Fill in the repository details:

- **Repository name:** `amu-pay` (or your preferred name)
- **Description:** `AMU Pay - Django Payment Application`
- **Visibility:**
  - **Public** - Anyone can see (free)
  - **Private** - Only you/team can see (recommended for production code)
- **Initialize repository:**
  - ❌ **DO NOT** check "Add a README file"
  - ❌ **DO NOT** check "Add .gitignore"
  - ❌ **DO NOT** check "Choose a license"
  
  (We already have these files)

4. Click **"Create repository"**

### Step 4: Copy Repository URL

After creating, GitHub will show you the repository URL. Copy it:

- **HTTPS:** `https://github.com/your-username/amu-pay.git`
- **SSH:** `git@github.com:your-username/amu-pay.git`

**Note:** We'll use HTTPS for this guide (easier for beginners).

---

## Initialize Git Repository

### Step 1: Navigate to Project Directory

Open PowerShell or Command Prompt and navigate to your project:

```bash
cd "C:\Users\Dell.com\Desktop\deploy finali\amu_pay13.1"
```

**Verify you're in the correct directory:**
```bash
# Should see amu_pay directory
dir amu_pay
```

### Step 2: Initialize Git Repository

**Option A: Using the Automated Script (Recommended)**

Run the provided PowerShell script:

```powershell
.\push_to_github.ps1
```

The script will guide you through the entire process.

**Option B: Manual Setup**

```bash
git init
```

Expected output:
```
Initialized empty Git repository in C:/Users/Dell.com/Desktop/deploy finali/amu_pay13.1/.git/
```

### Step 3: Configure Git (If Not Already Done)

Set your name and email (GitHub will use this for commits):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**Verify configuration:**
```bash
git config --global user.name
git config --global user.email
```

---

## Add Files to Git

### Step 1: Check Current Status

```bash
git status
```

This shows:
- **Untracked files** (files not yet added to Git)
- **Changes** (modified files)

### Step 2: Add All Files

```bash
# Add all files (respects .gitignore)
git add .
```

**Verify what will be committed:**
```bash
git status
```

You should see:
- ✅ Files listed under "Changes to be committed"
- ❌ `.env` file should NOT appear (it's in .gitignore)
- ❌ `venv/` should NOT appear (it's in .gitignore)

### Step 3: Verify Sensitive Files Are Excluded

Double-check that sensitive files are NOT being added:

```bash
# Check if .env is being tracked (should return nothing)
git ls-files | findstr ".env"

# Check for any .pem files (should return nothing)
git ls-files | findstr ".pem"
```

If these commands return files, they're being tracked. See [Troubleshooting](#troubleshooting) section.

---

## Create Initial Commit

### Step 1: Create Commit

```bash
git commit -m "Initial commit: AMU Pay Django application with EC2 deployment setup"
```

**Commit message best practices:**
- Use clear, descriptive messages
- First commit: "Initial commit: [project description]"
- Future commits: "Add feature X", "Fix bug Y", "Update documentation"

### Step 2: Verify Commit

```bash
git log --oneline
```

Should show:
```
[commit-hash] Initial commit: AMU Pay Django application with EC2 deployment setup
```

---

## Connect to GitHub

### Step 1: Add Remote Repository

Replace `your-username` and `amu-pay` with your actual GitHub username and repository name:

```bash
git remote add origin https://github.com/your-username/amu-pay.git
```

**Verify remote was added:**
```bash
git remote -v
```

Should show:
```
origin  https://github.com/your-username/amu-pay.git (fetch)
origin  https://github.com/your-username/amu-pay.git (push)
```

### Step 2: Rename Default Branch (Optional but Recommended)

GitHub uses `main` as default branch name:

```bash
git branch -M main
```

---

## Push to GitHub

### Step 1: Authenticate with GitHub

GitHub requires authentication. You have two options:

#### Option A: Personal Access Token (Recommended)

1. **Create Personal Access Token:**
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a name: "AMU Pay Project"
   - Select scopes: Check **"repo"** (full control of private repositories)
   - Click "Generate token"
   - **Copy the token immediately** (you won't see it again!)

2. **Use token as password:**
   - When you push, GitHub will ask for username and password
   - Username: Your GitHub username
   - Password: **Paste your Personal Access Token** (not your GitHub password)

#### Option B: GitHub CLI (Alternative)

```bash
# Install GitHub CLI
# Download from: https://cli.github.com/

# Authenticate
gh auth login
```

### Step 2: Push to GitHub

```bash
git push -u origin main
```

**If prompted for credentials:**
- **Username:** Your GitHub username
- **Password:** Your Personal Access Token (not your GitHub password)

**Expected output:**
```
Enumerating objects: XXX, done.
Counting objects: 100% (XXX/XXX), done.
Delta compression using up to X threads
Compressing objects: 100% (XXX/XXX), done.
Writing objects: 100% (XXX/XXX), XXX.XX KiB | XXX.XX MiB/s, done.
Total XXX (delta XXX), reused 0 (delta 0), pack-reused 0
To https://github.com/your-username/amu-pay.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

### Step 3: If Push Fails

**Error: "remote: Support for password authentication was removed"**

This means you need to use a Personal Access Token. See Step 1 above.

**Error: "Permission denied"**

- Check your username and token are correct
- Verify repository exists on GitHub
- Check if repository is private and you have access

---

## Verify Upload

### Step 1: Check GitHub Website

1. Go to your repository on GitHub:
   ```
   https://github.com/your-username/amu-pay
   ```

2. Verify you see:
   - ✅ All project files
   - ✅ `.gitignore` file
   - ✅ `README.md` (if you have one)
   - ✅ `env.example` file
   - ❌ **NO** `.env` file (should not be visible)
   - ❌ **NO** `venv/` directory

### Step 2: Verify from Command Line

```bash
# Check remote repository
git remote -v

# Check branch
git branch -a

# Fetch latest from GitHub
git fetch origin

# Compare local and remote
git status
```

Should show: "Your branch is up to date with 'origin/main'"

---

## Best Practices

### 1. Commit Frequently

Make small, logical commits:

```bash
# Good commit messages
git commit -m "Add RDS database configuration"
git commit -m "Update deployment documentation"
git commit -m "Fix nginx configuration path"

# Bad commit messages
git commit -m "update"
git commit -m "fix"
git commit -m "changes"
```

### 2. Use Branches for Features

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push branch
git push -u origin feature/new-feature

# Merge to main (on GitHub or locally)
git checkout main
git merge feature/new-feature
```

### 3. Keep .env File Safe

**Never commit `.env` file!**

- ✅ Keep `.env` in `.gitignore`
- ✅ Use `env.example` as template
- ✅ Document required variables in README

### 4. Regular Updates

```bash
# Pull latest changes (if working with team)
git pull origin main

# Push your changes
git add .
git commit -m "Your commit message"
git push origin main
```

### 5. Create README.md

Create a comprehensive README for your repository:

```bash
# Create README.md in project root
```

See example README structure below.

---

## Create README.md

Create a `README.md` file in your project root:

```markdown
# AMU Pay

Django-based payment application with exchange, hawala, and messaging features.

## Features

- User authentication and authorization
- Currency exchange management
- Hawala transaction system
- Real-time messaging
- WhatsApp and SMS OTP verification
- AI-powered assistance

## Tech Stack

- Django 5.2.6
- Django REST Framework
- MySQL (Amazon RDS)
- Gunicorn
- Nginx
- Twilio (SMS/WhatsApp)

## Installation

See [COMPLETE_DEPLOYMENT_GUIDE.md](COMPLETE_DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

## Quick Start

1. Clone repository
2. Copy `env.example` to `.env` and configure
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

## Documentation

- [Complete Deployment Guide](COMPLETE_DEPLOYMENT_GUIDE.md)
- [RDS Setup Guide](RDS_SETUP.md)
- [Quick Start Guide](QUICK_START.md)

## License

[Your License]
```

Then commit it:

```bash
git add README.md
git commit -m "Add README.md with project documentation"
git push origin main
```

---

## Troubleshooting

### Problem: ".env file is being tracked"

**Solution:**

```bash
# Remove .env from Git tracking (but keep local file)
git rm --cached .env

# Verify .env is in .gitignore
cat .gitignore | findstr ".env"

# Commit the removal
git commit -m "Remove .env from version control"

# Push changes
git push origin main
```

### Problem: "Large files won't upload"

**Solution:**

GitHub has a 100MB file size limit. For larger files:

1. **Remove large files:**
   ```bash
   git rm --cached large-file.zip
   git commit -m "Remove large file"
   ```

2. **Use Git LFS (Large File Storage):**
   ```bash
   git lfs install
   git lfs track "*.zip"
   git add .gitattributes
   ```

3. **Or use external storage** (AWS S3, etc.)

### Problem: "Authentication failed"

**Solutions:**

1. **Use Personal Access Token** instead of password
2. **Check token has 'repo' scope**
3. **Verify repository URL is correct**
4. **Try SSH instead of HTTPS:**
   ```bash
   git remote set-url origin git@github.com:your-username/amu-pay.git
   ```

### Problem: "Branch name mismatch"

**Solution:**

```bash
# Rename local branch
git branch -M main

# Or push with different name
git push -u origin main:master
```

### Problem: "Merge conflicts"

**Solution:**

```bash
# Pull latest changes
git pull origin main

# Resolve conflicts in files
# Then:
git add .
git commit -m "Resolve merge conflicts"
git push origin main
```

### Problem: "Accidentally committed sensitive data"

**Solution:**

1. **Remove from Git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

2. **Force push (WARNING: This rewrites history):**
   ```bash
   git push origin --force --all
   ```

3. **Rotate all exposed credentials immediately!**

---

## Common Git Commands Reference

```bash
# Check status
git status

# Add files
git add .                    # Add all files
git add filename.py          # Add specific file

# Commit
git commit -m "Message"

# Push
git push origin main

# Pull
git pull origin main

# Create branch
git checkout -b branch-name

# Switch branch
git checkout branch-name

# View commits
git log --oneline

# View changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

---

## Next Steps After Pushing

1. **Set up GitHub Actions** (CI/CD)
2. **Add repository description** on GitHub
3. **Create issues** for bugs/features
4. **Set up branch protection** (for main branch)
5. **Add collaborators** (if working with team)
6. **Enable GitHub Pages** (if needed for documentation)

---

## Security Checklist

Before pushing, ensure:

- [ ] `.env` file is in `.gitignore`
- [ ] No `.pem` or `.key` files are committed
- [ ] No passwords or API keys in code
- [ ] `env.example` has placeholder values only
- [ ] Database credentials are not in code
- [ ] Personal Access Token is stored securely (not in code)

---

## Summary

You've successfully pushed your AMU Pay project to GitHub! 

**What you accomplished:**
1. ✅ Created GitHub repository
2. ✅ Initialized Git repository
3. ✅ Added all project files (excluding sensitive files)
4. ✅ Created initial commit
5. ✅ Pushed to GitHub
6. ✅ Verified upload

**Your repository is now available at:**
```
https://github.com/your-username/amu-pay
```

**For future updates:**
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

---

**Need Help?**
- GitHub Documentation: https://docs.github.com/
- Git Documentation: https://git-scm.com/doc
- GitHub Support: https://support.github.com/

---

**Last Updated:** 2024

