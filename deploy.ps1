param (
    [switch]$Preview,
    [switch]$Yes
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   BẮT ĐẦU DEPLOY LÊN VERCEL BẰNG CLI" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Kiểm tra xem Vercel CLI đã được cài đặt chưa
if (!(Get-Command vercel -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Vercel CLI chưa được cài đặt. Đang tiến hành cài đặt..." -ForegroundColor Yellow
    npm install -g vercel
}

# Các cờ dòng lệnh
$VercelArgs = @()

if ($Yes) {
    $VercelArgs += "--yes"
}

if ($Preview) {
    Write-Host "[+] Đang deploy bản Preview..." -ForegroundColor Green
    # Preview deployment
    vercel @VercelArgs
} else {
    Write-Host "[+] Đang deploy bản Production (--prod)..." -ForegroundColor Green
    # Production deployment
    vercel --prod @VercelArgs
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "   DEPLOY THÀNH CÔNG!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
} else {
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "   DEPLOY THẤT BẠI. Vui lòng kiểm tra log!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
}
