# Recria o atalho de auto-start na pasta Startup e inicia o widget agora.
# Uso: powershell -ExecutionPolicy Bypass -File install.ps1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonw = 'C:\Python314\pythonw.exe'
if (-not (Test-Path $pythonw)) { $pythonw = (Get-Command pythonw.exe).Source }

$ws = New-Object -ComObject WScript.Shell
$lnk = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup\Claude Usage Monitor.lnk'
$s = $ws.CreateShortcut($lnk)
$s.TargetPath = $pythonw
$s.Arguments = 'widget.pyw'
$s.WorkingDirectory = $here
$s.Description = 'Widget de uso do plano Claude'
$s.Save()
Write-Host "Atalho recriado: $lnk"

# Instância única (porta 53764) impede duplicar se já estiver rodando
Start-Process -FilePath $pythonw -ArgumentList 'widget.pyw' -WorkingDirectory $here
Write-Host 'Widget iniciado.'
