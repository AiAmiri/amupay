# PowerShell script to deploy code to AWS EC2 server
# Usage: .\deploy_to_aws.ps1 -ServerIP "your-server-ip" -KeyPath "path\to\your-key.pem"

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerIP,
    
    [Parameter(Mandatory=$true)]
    [string]$KeyPath,
    
    [string]$ServerUser = "ubuntu",
    [string]$RemotePath = "/home/ubuntu/amupay/amu_pay"
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deploying to AWS Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if key file exists
if (-not (Test-Path $KeyPath)) {
    Write-Host "Error: Key file not found at $KeyPath" -ForegroundColor Red
    exit 1
}

# Files to deploy
$filesToDeploy = @(
    "amu_pay\amu_pay\settings.py",
    "test_db_connection.py"
)

Write-Host "`nCopying files to server..." -ForegroundColor Yellow

foreach ($file in $filesToDeploy) {
    if (Test-Path $file) {
        $remoteFile = if ($file -like "amu_pay\*") {
            "$RemotePath/amu_pay/settings.py"
        } else {
            "/home/ubuntu/amupay/$file"
        }
        
        Write-Host "  Copying $file..." -ForegroundColor Gray
        scp -i $KeyPath $file "${ServerUser}@${ServerIP}:$remoteFile"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ $file copied successfully" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Failed to copy $file" -ForegroundColor Red
        }
    } else {
        Write-Host "  ⚠ Warning: $file not found, skipping..." -ForegroundColor Yellow
    }
}

Write-Host "`nFiles copied. Now connecting to server to deploy..." -ForegroundColor Yellow
Write-Host "You will need to run these commands on the server:" -ForegroundColor Cyan
Write-Host "  cd /home/ubuntu/amupay/amu_pay" -ForegroundColor White
Write-Host "  source ../amu_pay_env/bin/activate" -ForegroundColor White
Write-Host "  sudo systemctl restart amu_pay" -ForegroundColor White
Write-Host "  sudo systemctl status amu_pay" -ForegroundColor White

# Optionally, SSH into the server
$ssh = Read-Host "`nDo you want to SSH into the server now? (y/n)"
if ($ssh -eq "y" -or $ssh -eq "Y") {
    Write-Host "Connecting to server..." -ForegroundColor Yellow
    ssh -i $KeyPath "${ServerUser}@${ServerIP}"
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Deployment script completed!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

