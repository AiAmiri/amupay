@echo off
REM Batch script to deploy code to AWS EC2 server
REM Usage: deploy_to_aws.bat

echo =========================================
echo Deploying to AWS Server
echo =========================================
echo.

set /p SERVER_IP="Enter your server IP or domain: "
set /p KEY_PATH="Enter path to your .pem key file: "
set /p SERVER_USER="Enter server username (default: ubuntu): "

if "%SERVER_USER%"=="" set SERVER_USER=ubuntu

echo.
echo Copying files to server...
echo.

REM Copy settings.py
if exist "amu_pay\amu_pay\settings.py" (
    echo Copying settings.py...
    scp -i "%KEY_PATH%" "amu_pay\amu_pay\settings.py" %SERVER_USER%@%SERVER_IP%:/home/ubuntu/amupay/amu_pay/amu_pay/
    if %ERRORLEVEL% EQU 0 (
        echo [OK] settings.py copied successfully
    ) else (
        echo [ERROR] Failed to copy settings.py
    )
) else (
    echo [WARNING] settings.py not found
)

REM Copy test_db_connection.py
if exist "test_db_connection.py" (
    echo Copying test_db_connection.py...
    scp -i "%KEY_PATH%" "test_db_connection.py" %SERVER_USER%@%SERVER_IP%:/home/ubuntu/amupay/
    if %ERRORLEVEL% EQU 0 (
        echo [OK] test_db_connection.py copied successfully
    ) else (
        echo [ERROR] Failed to copy test_db_connection.py
    )
) else (
    echo [WARNING] test_db_connection.py not found
)

echo.
echo =========================================
echo Files copied!
echo =========================================
echo.
echo Next steps:
echo 1. SSH into your server:
echo    ssh -i "%KEY_PATH%" %SERVER_USER%@%SERVER_IP%
echo.
echo 2. Run these commands on the server:
echo    cd /home/ubuntu/amupay/amu_pay
echo    source ../amu_pay_env/bin/activate
echo    sudo systemctl restart amu_pay
echo    sudo systemctl status amu_pay
echo.

pause

