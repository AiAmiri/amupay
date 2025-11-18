# How to Run the PowerShell Script

## Common Errors and Solutions

### Error 1: "Cannot run script - execution policy"

**Solution:**
```powershell
# Check current execution policy
Get-ExecutionPolicy

# If it's "Restricted", run this (as Administrator):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run the script with bypass:
powershell -ExecutionPolicy Bypass -File .\push_to_github.ps1
```

### Error 2: "File not found" or "Cannot find path"

**Solution:**
Make sure you're in the correct directory:
```powershell
# Navigate to project directory
cd "C:\Users\Dell.com\Desktop\deploy finali\amu_pay13.1"

# Verify you're in the right place
dir amu_pay
dir push_to_github.ps1
```

### Error 3: Script runs but shows errors

**Solution:** Use the simpler version:
```powershell
.\push_to_github_simple.ps1
```

---

## How to Run the Script

### Method 1: Direct Execution (Recommended)

1. **Open PowerShell** (not Command Prompt)
2. **Navigate to project directory:**
   ```powershell
   cd "C:\Users\Dell.com\Desktop\deploy finali\amu_pay13.1"
   ```

3. **Run the script:**
   ```powershell
   .\push_to_github.ps1
   ```

   Or use the simple version:
   ```powershell
   .\push_to_github_simple.ps1
   ```

### Method 2: With Execution Policy Bypass

If you get execution policy errors:

```powershell
powershell -ExecutionPolicy Bypass -File ".\push_to_github.ps1"
```

### Method 3: Right-Click Method

1. **Right-click** on `push_to_github.ps1` in File Explorer
2. Select **"Run with PowerShell"**
3. If it doesn't work, use Method 1 or 2

### Method 4: From File Explorer

1. Open File Explorer
2. Navigate to: `C:\Users\Dell.com\Desktop\deploy finali\amu_pay13.1`
3. In the address bar, type: `powershell` and press Enter
4. Run: `.\push_to_github.ps1`

---

## Step-by-Step Manual Alternative

If the script still doesn't work, follow these manual steps:

### 1. Open PowerShell in Project Directory

```powershell
cd "C:\Users\Dell.com\Desktop\deploy finali\amu_pay13.1"
```

### 2. Initialize Git

```powershell
git init
```

### 3. Configure Git (First Time Only)

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 4. Add Files

```powershell
git add .
```

### 5. Create Commit

```powershell
git commit -m "Initial commit: AMU Pay Django application"
```

### 6. Add Remote Repository

```powershell
git remote add origin https://github.com/your-username/amu-pay.git
```

### 7. Rename Branch

```powershell
git branch -M main
```

### 8. Push to GitHub

```powershell
git push -u origin main
```

When prompted:
- **Username:** Your GitHub username
- **Password:** Your Personal Access Token (not your GitHub password)

---

## Troubleshooting

### Script Won't Run at All

**Check PowerShell version:**
```powershell
$PSVersionTable.PSVersion
```

Should be 5.1 or higher. If not, update Windows.

**Check if script exists:**
```powershell
Test-Path ".\push_to_github.ps1"
```

Should return `True`.

### Script Runs But Stops Early

**Check for errors:**
- Read the error message carefully
- Common issues:
  - Git not installed
  - Wrong directory
  - Network issues

### Authentication Errors

**Create Personal Access Token:**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "AMU Pay Project"
4. Check "repo" scope
5. Generate and copy token
6. Use token as password when pushing

---

## Quick Test

Test if everything is set up correctly:

```powershell
# Check Git
git --version

# Check directory
Get-Location
dir amu_pay

# Check script
Test-Path ".\push_to_github.ps1"
```

All should return successfully.

---

## Still Having Issues?

1. **Use the simple script:** `push_to_github_simple.ps1`
2. **Follow manual steps** above
3. **Check the full guide:** `GITHUB_DEPLOYMENT_GUIDE.md`

---

## Alternative: Use Git Bash

If PowerShell continues to have issues, use Git Bash:

1. **Open Git Bash** (installed with Git)
2. **Navigate to project:**
   ```bash
   cd "/c/Users/Dell.com/Desktop/deploy finali/amu_pay13.1"
   ```

3. **Follow manual steps** (same Git commands work in Git Bash)

