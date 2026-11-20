[CmdletBinding()]
param(
    [int]$ListenPort = 8090,
    [int]$ConnectPort = 8090,
    [string]$WslDistro = "",
    [string]$FirewallRuleName = "home-node-linux 8090",
    [string]$TestProject = "household"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Проверка прав администратора
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Запустите этот скрипт в PowerShell от имени Администратора."
}

# Получаем текущий IPv4 внутри WSL2
$wslArgs = @()
if ($WslDistro) {
    $wslArgs += @("-d", $WslDistro)
}
$wslArgs += @("-e", "hostname", "-I")

$rawWslIps = (& wsl.exe @wslArgs) -join " "
$wslIp = ($rawWslIps -split "\s+" | Where-Object {
    $_ -match "^(172\.(1[6-9]|2\d|3[0-1])\.|10\.|192\.168\.)"
} | Select-Object -First 1)

if (-not $wslIp) {
    $wslIp = ($rawWslIps -split "\s+" | Where-Object { $_ -match "^\d{1,3}(\.\d{1,3}){3}$" } | Select-Object -First 1)
}

if (-not $wslIp) {
    throw "Не удалось определить IPv4 адрес WSL2 из вывода: '$rawWslIps'"
}

Write-Host "Актуальный IP WSL2: $wslIp" -ForegroundColor Cyan

# Пересоздаём правило portproxy на нужный порт
& netsh.exe interface portproxy delete v4tov4 listenport=$ListenPort listenaddress=0.0.0.0 2>$null | Out-Null
& netsh.exe interface portproxy add v4tov4 listenport=$ListenPort listenaddress=0.0.0.0 connectport=$ConnectPort connectaddress=$wslIp | Out-Null

# Проверяем / создаём правило брандмауэра Windows
$existingRule = Get-NetFirewallRule -DisplayName $FirewallRuleName -ErrorAction SilentlyContinue
if (-not $existingRule) {
    New-NetFirewallRule `
        -DisplayName $FirewallRuleName `
        -Direction Inbound `
        -LocalPort $ListenPort `
        -Protocol TCP `
        -Action Allow `
        -Profile Any | Out-Null
    Write-Host "Добавлено правило брандмауэра: '$FirewallRuleName' (TCP $ListenPort)." -ForegroundColor Green
} else {
    Write-Host "Правило брандмауэра '$FirewallRuleName' уже существует." -ForegroundColor Green
}

# Определяем IPv4 Windows для подключения с Android (LAN / точка доступа / VPN)
$windowsIps = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Where-Object {
    $_.IPAddress -notmatch "^127\." -and
    $_.IPAddress -notmatch "^169\.254\." -and
    $_.IPAddress -notmatch "^172\.(1[6-9]|2\d|3[0-1])\."
} | Select-Object -ExpandProperty IPAddress -Unique

Write-Host "`nТекущие правила portproxy (порт $ListenPort):" -ForegroundColor Yellow
& netsh.exe interface portproxy show v4tov4 | Select-String -Pattern "(Address|---|\b$ListenPort\b)"

Write-Host "`nПроверьте подключение с Android по одному из адресов:" -ForegroundColor Cyan
foreach ($ip in $windowsIps) {
    Write-Host "  Health : http://$ip`:$ListenPort/health"
    Write-Host "  Ping   : http://$ip`:$ListenPort/api/v1/projects/$TestProject/ping"
}