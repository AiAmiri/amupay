# GitHub Push - Quick Reference

## 🚀 Quick Start (Automated)

```powershell
# Run from project root directory
.\push_to_github.ps1
```

## 📋 Manual Steps

### 1. Create GitHub Repository
- Go to https://github.com/new
- Name: `amu-pay`
- Visibility: Private (recommended)
- **Don't** initialize with README

### 2. Initialize Git

```bash
# Navigate to project
cd "C:\Users\Dell.com\Desktop\deploy finali\amu_pay13.1"

# Initialize Git
git init

# Configure Git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Add Files

```bash
# Add all files
git add .

# Verify .env is NOT being added
git status
```

### 4. Create Commit

```bash
git commit -m "Initial commit: AMU Pay Django application"
```

### 5. Connect to GitHub

```bash
# Add remote (replace with your repository URL)
git remote add origin https://github.com/your-username/amu-pay.git

# Rename branch
git branch -M main
```

### 6. Push to GitHub

```bash
git push -u origin main
```

**When prompted:**
- Username: Your GitHub username
- Password: **Personal Access Token** (not your password!)

## 🔑 Create Personal Access Token

1. GitHub → Settings → Developer settings
2. Personal access tokens → Tokens (classic)
3. Generate new token (classic)
4. Name: "AMU Pay Project"
5. Scope: Check **"repo"**
6. Generate and **copy token immediately**

## ✅ Verify Upload

Visit: `https://github.com/your-username/amu-pay`

Check:
- ✅ All files are visible
- ❌ `.env` file is NOT visible
- ❌ `venv/` is NOT visible

## 🔄 Future Updates

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

## ⚠️ Important

- **Never commit `.env` file**
- **Never commit `.pem` or `.key` files**
- **Use Personal Access Token, not password**

## 📚 Full Guide

See `GITHUB_DEPLOYMENT_GUIDE.md` for complete instructions.

