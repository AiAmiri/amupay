# PowerShell Script to Push AMU Pay Project to GitHub
# Run this script from the project root directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AMU Pay - GitHub Push Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is installed
Write-Host "Checking Git installation..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "✓ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "amu_pay")) {
    Write-Host "✗ Error: 'amu_pay' directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory" -ForegroundColor Yellow
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Project directory found" -ForegroundColor Green
Write-Host ""

# Check if .gitignore exists
if (-not (Test-Path ".gitignore")) {
    Write-Host "✗ Warning: .gitignore file not found!" -ForegroundColor Yellow
    Write-Host "Creating .gitignore..." -ForegroundColor Yellow
    # .gitignore should already exist, but just in case
}

# Check if .env file exists and warn
if (Test-Path ".env") {
    Write-Host "⚠ Warning: .env file found" -ForegroundColor Yellow
    Write-Host "Make sure .env is in .gitignore before proceeding!" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Aborted by user" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Initialize Git repository (if not already initialized)
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✓ Git repository already initialized" -ForegroundColor Green
}

Write-Host ""

# Configure Git user (if not configured)
Write-Host "Checking Git configuration..." -ForegroundColor Yellow
$gitUser = git config --global user.name
$gitEmail = git config --global user.email

if (-not $gitUser) {
    Write-Host "Git user name not configured" -ForegroundColor Yellow
    $userName = Read-Host "Enter your name for Git commits"
    git config --global user.name $userName
    Write-Host "✓ Git user name configured" -ForegroundColor Green
}

if (-not $gitEmail) {
    Write-Host "Git email not configured" -ForegroundColor Yellow
    $userEmail = Read-Host "Enter your email for Git commits"
    git config --global user.email $userEmail
    Write-Host "✓ Git email configured" -ForegroundColor Green
}

Write-Host ""

# Check current status
Write-Host "Checking Git status..." -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "Files to be added:" -ForegroundColor Cyan
git status --porcelain | Where-Object { $_ -match "^[AM]" } | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Gray
}

Write-Host ""

# Ask for confirmation
$confirm = Read-Host "Add all files and create initial commit? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Aborted by user" -ForegroundColor Red
    exit 1
}

# Add all files
Write-Host ""
Write-Host "Adding files to Git..." -ForegroundColor Yellow
git add .

# Verify .env is not being tracked
$envTracked = git ls-files | Select-String ".env"
if ($envTracked) {
    Write-Host ""
    Write-Host "✗ WARNING: .env file is being tracked!" -ForegroundColor Red
    Write-Host "Removing .env from Git tracking..." -ForegroundColor Yellow
    git rm --cached .env
    Write-Host "Please ensure .env is in .gitignore" -ForegroundColor Yellow
}

Write-Host "✓ Files added" -ForegroundColor Green

# Create commit
Write-Host ""
Write-Host "Creating initial commit..." -ForegroundColor Yellow
$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Initial commit: AMU Pay Django application with EC2 deployment setup"
}

git commit -m $commitMessage
Write-Host "✓ Commit created" -ForegroundColor Green

Write-Host ""

# Ask about remote repository
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Before pushing, you need to:" -ForegroundColor Yellow
Write-Host "1. Create a repository on GitHub" -ForegroundColor White
Write-Host "2. Get the repository URL" -ForegroundColor White
Write-Host ""

$hasRemote = git remote -v
if ($hasRemote) {
    Write-Host "Current remote repository:" -ForegroundColor Cyan
    git remote -v
    Write-Host ""
    $changeRemote = Read-Host "Change remote repository? (y/n)"
    if ($changeRemote -eq "y") {
        git remote remove origin
        $hasRemote = $null
    }
}

if (-not $hasRemote) {
    Write-Host "Enter your GitHub repository URL:" -ForegroundColor Yellow
    Write-Host "Example: https://github.com/your-username/amu-pay.git" -ForegroundColor Gray
    $repoUrl = Read-Host "Repository URL"
    
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "✓ Remote repository added" -ForegroundColor Green
    } else {
        Write-Host "⚠ No repository URL provided. You can add it later with:" -ForegroundColor Yellow
        Write-Host "  git remote add origin <repository-url>" -ForegroundColor Gray
    }
}

Write-Host ""

# Rename branch to main
Write-Host "Setting branch name to 'main'..." -ForegroundColor Yellow
git branch -M main
Write-Host "✓ Branch renamed to 'main'" -ForegroundColor Green

Write-Host ""

# Push to GitHub
$push = Read-Host "Push to GitHub now? (y/n)"
if ($push -eq "y") {
    Write-Host ""
    Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
    Write-Host "Note: You may be prompted for GitHub credentials" -ForegroundColor Yellow
    Write-Host "Use your Personal Access Token as password (not your GitHub password)" -ForegroundColor Yellow
    Write-Host ""
    
    try {
        git push -u origin main
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "✓ Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    } catch {
        Write-Host ""
        Write-Host "✗ Push failed!" -ForegroundColor Red
        Write-Host "Common issues:" -ForegroundColor Yellow
        Write-Host "1. Repository doesn't exist on GitHub" -ForegroundColor White
        Write-Host "2. Authentication failed (use Personal Access Token)" -ForegroundColor White
        Write-Host "3. Wrong repository URL" -ForegroundColor White
        Write-Host ""
        Write-Host "See GITHUB_DEPLOYMENT_GUIDE.md for troubleshooting" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "To push later, run:" -ForegroundColor Yellow
    Write-Host "  git push -u origin main" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Script completed!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Verify files on GitHub website" -ForegroundColor White
Write-Host "2. Ensure .env file is NOT visible on GitHub" -ForegroundColor White
Write-Host "3. Check GITHUB_DEPLOYMENT_GUIDE.md for more details" -ForegroundColor White
Write-Host ""

