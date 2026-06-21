@echo off
echo ==========================================
echo    BAT DAU DEPLOY LEN VERCEL BANG CLI
echo ==========================================

:: Kiem tra Vercel CLI
where vercel >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Vercel CLI chua duoc cai dat. Dang tien hanh cai dat...
    call npm install -g vercel
)

set ARGS=

:parse_args
if "%~1"=="" goto run_deploy
if /I "%~1"=="--preview" set PREVIEW=1
if /I "%~1"=="--yes" set ARGS=%ARGS% --yes
shift
goto parse_args

:run_deploy
if defined PREVIEW (
    echo [+] Dang deploy ban Preview...
    call vercel %ARGS%
) else (
    echo [+] Dang deploy ban Production (--prod)...
    call vercel --prod %ARGS%
)

if %errorlevel% equ 0 (
    echo ==========================================
    echo    DEPLOY THANH CONG!
    echo ==========================================
) else (
    echo ==========================================
    echo    DEPLOY THAT BAI. Vui long kiem tra log!
    echo ==========================================
)
