param([string]$Installer = "$PSScriptRoot\..\release\ParsecChineseLocalization-0.1.0-windows-x64-setup.exe")
$ErrorActionPreference = 'Stop'
$taskInstallRoot = Join-Path $env:TEMP ('pcl-install-test-' + [guid]::NewGuid().ToString('N'))
# Installer /DIR is isolated. No user installation or Parsec file is used.
$taskSetup = Start-Process -FilePath (Resolve-Path -LiteralPath $Installer).Path -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',"/DIR=`"$taskInstallRoot`"",'/GROUP=Parsec Chinese Localization Test') -Wait -PassThru -WindowStyle Hidden
if ($taskSetup.ExitCode -ne 0) { throw "Installer failed: $($taskSetup.ExitCode)" }
$taskExe = Join-Path $taskInstallRoot 'ParsecChineseLocalization.exe'
if (!(Test-Path -LiteralPath $taskExe)) { throw 'Installed executable missing' }
$taskSmoke = Start-Process -FilePath $taskExe -ArgumentList '--smoke-test' -Wait -PassThru -WindowStyle Hidden
if ($taskSmoke.ExitCode -ne 0) { throw "Installed smoke test failed: $($taskSmoke.ExitCode)" }
# Do not remove a user's preferences when testing an isolated installation.
$taskUninstall = Start-Process -FilePath (Join-Path $taskInstallRoot 'unins000.exe') -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/KEEPPREFERENCES') -Wait -PassThru -WindowStyle Hidden
if ($taskUninstall.ExitCode -ne 0) { throw "Uninstall failed: $($taskUninstall.ExitCode)" }
if (Test-Path -LiteralPath $taskExe) { throw 'Uninstall left the application executable behind' }
Write-Output 'PASS: install, installed GUI smoke test, uninstall'
