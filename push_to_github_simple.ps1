# Simple PowerShell Script to Push AMU Pay Project to GitHub
# Run this script from the project root directory

# Check if Git is installed
Write-Host "Checking Git installation..." -ForegroundColor Yellow
$gitCheck = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCheck) {
    Write-Host "ERROR: Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "Git is installed: $(git --version)" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "amu_pay")) {
    Write-Host "ERROR: 'amu_pay' directory not found!" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Please run this script from the project root directory" -ForegroundColor Yellow
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "Project directory found" -ForegroundColor Green
Write-Host ""

# Initialize Git repository (if not already initialized)
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "Git repository already initialized" -ForegroundColor Green
}

Write-Host ""

# Configure Git user (if not configured)
$gitUser = git config --global user.name 2>$null
$gitEmail = git config --global user.email 2>$null

if (-not $gitUser) {
    Write-Host "Git user name not configured" -ForegroundColor Yellow
    $userName = Read-Host "Enter your name for Git commits"
    if ($userName) {
        git config --global user.name $userName
        Write-Host "Git user name configured" -ForegroundColor Green
    }
}

if (-not $gitEmail) {
    Write-Host "Git email not configured" -ForegroundColor Yellow
    $userEmail = Read-Host "Enter your email for Git commits"
    if ($userEmail) {
        git config --global user.email $userEmail
        Write-Host "Git email configured" -ForegroundColor Green
    }
}

Write-Host ""

# Add all files
Write-Host "Adding files to Git..." -ForegroundColor Yellow
git add .

# Check if .env is being tracked
$envTracked = git ls-files 2>$null | Select-String ".env"
if ($envTracked) {
    Write-Host ""
    Write-Host "WARNING: .env file is being tracked!" -ForegroundColor Red
    Write-Host "Removing .env from Git tracking..." -ForegroundColor Yellow
    git rm --cached .env 2>$null
}

Write-Host "Files added" -ForegroundColor Green
Write-Host ""

# Create commit
Write-Host "Creating initial commit..." -ForegroundColor Yellow
$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Initial commit: AMU Pay Django application with EC2 deployment setup"
}

git commit -m $commitMessage
if ($LASTEXITCODE -eq 0) {
    Write-Host "Commit created successfully" -ForegroundColor Green
} else {
    Write-Host "Commit failed. Check if there are files to commit." -ForegroundColor Yellow
}

Write-Host ""

# Ask about remote repository
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Before pushing, you need to:" -ForegroundColor Yellow
Write-Host "1. Create a repository on GitHub (https://github.com/new)" -ForegroundColor White
Write-Host "2. Get the repository URL" -ForegroundColor White
Write-Host ""

$hasRemote = git remote -v 2>$null
if ($hasRemote) {
    Write-Host "Current remote repository:" -ForegroundColor Cyan
    git remote -v
    Write-Host ""
    $changeRemote = Read-Host "Change remote repository? (y/n)"
    if ($changeRemote -eq "y") {
        git remote remove origin 2>$null
        $hasRemote = $null
    }
}

if (-not $hasRemote) {
    Write-Host "Enter your GitHub repository URL:" -ForegroundColor Yellow
    Write-Host "Example: https://github.com/your-username/amu-pay.git" -ForegroundColor Gray
    $repoUrl = Read-Host "Repository URL"
    
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "Remote repository added" -ForegroundColor Green
    } else {
        Write-Host "No repository URL provided. You can add it later with:" -ForegroundColor Yellow
        Write-Host "  git remote add origin <repository-url>" -ForegroundColor Gray
    }
}

Write-Host ""

# Rename branch to main
Write-Host "Setting branch name to 'main'..." -ForegroundColor Yellow
git branch -M main 2>$null
Write-Host "Branch set to 'main'" -ForegroundColor Green

Write-Host ""

# Push to GitHub
$push = Read-Host "Push to GitHub now? (y/n)"
if ($push -eq "y") {
    Write-Host ""
    Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
    Write-Host "Note: You will be prompted for GitHub credentials" -ForegroundColor Yellow
    Write-Host "Username: Your GitHub username" -ForegroundColor White
    Write-Host "Password: Use your Personal Access Token (NOT your GitHub password)" -ForegroundColor White
    Write-Host ""
    
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "Push failed!" -ForegroundColor Red
        Write-Host "Common issues:" -ForegroundColor Yellow
        Write-Host "1. Repository doesn't exist on GitHub" -ForegroundColor White
        Write-Host "2. Authentication failed (use Personal Access Token)" -ForegroundColor White
        Write-Host "3. Wrong repository URL" -ForegroundColor White
    }
} else {
    Write-Host ""
    Write-Host "To push later, run:" -ForegroundColor Yellow
    Write-Host "  git push -u origin main" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Script completed!" -ForegroundColor Cyan
Write-Host ""

