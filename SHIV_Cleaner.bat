@echo off
setlocal EnableExtensions EnableDelayedExpansion
title SHIV - Ultimate System Cleaner
color 0F
mode con: cols=100 lines=50 >nul 2>&1

:: ============================================================
::   SHIV ULTIMATE SYSTEM CLEANER  v1.0
::   Clean | Reset | Security | Pro Tools
::   Run as Administrator (script auto-elevates)
:: ============================================================

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator rights...
    powershell -nop -c "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

reg add "HKCU\Console" /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

set "_R=%ESC%[91m"
set "_G=%ESC%[92m"
set "_Y=%ESC%[93m"
set "_B=%ESC%[94m"
set "_M=%ESC%[95m"
set "_C=%ESC%[96m"
set "_W=%ESC%[97m"
set "_D=%ESC%[90m"
set "_X=%ESC%[0m"
set "LOG=%~dp0SHIV_Cleaner_Log.txt"
set "F1=0"
set "F2=0"
set "IND=                          "

:: ---- Rainbow palette (256-colour codes)
set "PAL=196 202 208 214 220 226 190 154 118 82 46 48 51 45 39 33 27 57 93 129 165 201 199"
set "PN=0"
for %%p in (%PAL%) do (
    set "p!PN!=%%p"
    set /a PN+=1
)

:: ---- Big block letters S H I V (each segment 12 chars wide)
set "S1=  ########  "
set "S2=##          "
set "S3=  ######    "
set "S4=        ##  "
set "S5=########    "
set "H1=##      ##  "
set "H2=##      ##  "
set "H3=##########  "
set "H4=##      ##  "
set "H5=##      ##  "
set "I1=##########  "
set "I2=    ##      "
set "I3=    ##      "
set "I4=    ##      "
set "I5=##########  "
set "V1=##      ##  "
set "V2=##      ##  "
set "V3=##      ##  "
set "V4=  ##  ##    "
set "V5=    ##      "
for %%r in (1 2 3 4 5) do set "ROW%%r=!S%%r!!H%%r!!I%%r!!V%%r!"

call :log "=== Session started ==="
call :intro
goto menu

:: ============================================================
::                      ANIMATED INTRO
:: ============================================================
:intro
cls
<nul set /p "=%ESC%[?25l"
echo.
for /l %%f in (1,1,36) do (
    <nul set /p "=%ESC%[2;1H"
    for /l %%r in (1,1,5) do (
        set /a "a1=(%%f+%%r*2) %% PN, a2=(%%f+%%r*2+6) %% PN, a3=(%%f+%%r*2+12) %% PN, a4=(%%f+%%r*2+18) %% PN"
        for /f "tokens=1-4" %%w in ("!a1! !a2! !a3! !a4!") do (
            set "LN=!IND!!ESC![38;5;!p%%w!m!S%%r!!ESC![38;5;!p%%x!m!H%%r!!ESC![38;5;!p%%y!m!I%%r!!ESC![38;5;!p%%z!m!V%%r!!_X!"
            echo(!LN!
            echo(!LN!
        )
    )
    call :sleep 30
)
echo.
<nul set /p "=!IND!%_C%"
call :typewriter "U L T I M A T E   S Y S T E M   C L E A N E R"
echo %_X%
echo.
call :progress "Loading modules   "
call :sleep 500
<nul set /p "=%ESC%[?25h"
exit /b

:typewriter
set "tw=%~1"
:tw_loop
if not defined tw exit /b
<nul set /p "=!tw:~0,1!"
set "tw=!tw:~1!"
call :sleep 18
goto tw_loop

:progress
<nul set /p "=!IND!%_W%%~1"
for /l %%i in (1,1,24) do (
    set /a pc=%%i*8+20
    <nul set /p "=!ESC![38;5;!pc!m#"
    call :sleep 25
)
echo %_X% done
exit /b

:sleep
ping 192.0.2.1 -n 1 -w %1 >nul 2>&1
exit /b

:: ============================================================
::                      STATIC BANNER
:: ============================================================
:banner_static
echo.
call :brow 1 196
call :brow 2 208
call :brow 3 226
call :brow 4 46
call :brow 5 51
exit /b

:brow
echo(!IND!!ESC![38;5;%2m!ROW%1!!_X!
echo(!IND!!ESC![38;5;%2m!ROW%1!!_X!
exit /b

:hdr
cls
call :banner_static
echo   %_M%  S H I V   U L T I M A T E   C L E A N E R%_X%
echo   %_D%  ------------------------------------------------------------%_X%
echo   %_Y%  %~1%_X%
echo.
exit /b

:: ============================================================
::                          MAIN MENU
:: ============================================================
:menu
cls
call :banner_static
echo   %_M%         U L T I M A T E   S Y S T E M   C L E A N E R   %_D%v1.0%_X%
echo   %_C%  ==============================================================================%_X%
echo   %_Y%  CLEAN%_X%
echo     %_G%[1]%_X% Quick Clean         %_D%Temp, %%TEMP%%, Recent, Prefetch%_X%
echo     %_G%[2]%_X% Windows Update      %_D%Update logs, SoftwareDistribution folder%_X%
echo     %_G%[3]%_X% Deep Clean          %_D%1 + 2 + Recycle Bin, Thumbnails, Browser cache, Dumps%_X%
echo   %_Y%  RESET  %_D%(optional)%_X%
echo     %_G%[4]%_X% Network Adapter     %_D%Winsock, TCP/IP stack, restart adapters%_X%
echo     %_G%[5]%_X% DNS Tools           %_D%Flush, reset to auto, Google DNS, Cloudflare DNS%_X%
echo   %_Y%  SECURITY%_X%
echo     %_G%[6]%_X% MRT Tool            %_D%Microsoft Malicious Software Removal Tool%_X%
echo     %_G%[7]%_X% Defender            %_D%Update signatures + Quick Scan%_X%
echo   %_Y%  PRO TOOLS%_X%
echo     %_G%[8]%_X% System Repair       %_D%SFC /scannow + DISM RestoreHealth%_X%
echo     %_G%[9]%_X% Disk Cleanup        %_D%Windows cleanmgr with your selection%_X%
echo     %_G%[A]%_X% System Information  %_D%OS, CPU, RAM, disks%_X%
echo     %_G%[B]%_X% Restore Point       %_D%Create a safety restore point%_X%
echo     %_G%[C]%_X% View Log            %_D%Open SHIV_Cleaner_Log.txt%_X%
echo     %_R%[0]%_X% Exit
echo   %_C%  ==============================================================================%_X%
echo.
set "opt="
set /p "opt=  %_C%SHIV%_W% ^>^> %_X%Select option: "
if /i "%opt%"=="1" goto do_quick
if /i "%opt%"=="2" goto do_update
if /i "%opt%"=="3" goto do_deep
if /i "%opt%"=="4" goto do_netreset
if /i "%opt%"=="5" goto do_dns
if /i "%opt%"=="6" goto do_mrt
if /i "%opt%"=="7" goto do_defender
if /i "%opt%"=="8" goto do_repair
if /i "%opt%"=="9" goto do_cleanmgr
if /i "%opt%"=="A" goto do_info
if /i "%opt%"=="B" goto do_restore
if /i "%opt%"=="C" goto do_log
if /i "%opt%"=="0" goto do_exit
goto menu

:done_pause
echo.
echo   %_D%Press any key to return to the menu...%_X%
pause >nul
goto menu

:: ============================================================
::                          CLEAN
:: ============================================================
:do_quick
call :hdr "QUICK CLEAN"
call :getfree F1
call :c_quick
call :report
goto done_pause

:do_update
call :hdr "WINDOWS UPDATE CLEAN"
echo   %_D%Note: update history resets after clearing SoftwareDistribution.%_X%
call :ask "Continue?"
if errorlevel 2 goto menu
call :getfree F1
call :c_update
call :report
goto done_pause

:do_deep
call :hdr "DEEP CLEAN"
echo   %_D%Tip: close browsers first for best results.%_X%
call :ask "Start deep clean?"
if errorlevel 2 goto menu
call :getfree F1
call :c_quick
call :c_update
call :c_extra
call :report
goto done_pause

:c_quick
echo   %_C%-- Temp / Recent / Prefetch --%_X%
call :wipe "%SystemRoot%\Temp" "Windows Temp folder"
call :wipe "%TEMP%" "User TEMP folder"
call :wipe "%APPDATA%\Microsoft\Windows\Recent" "Recent files and jump lists"
call :wipe "%SystemRoot%\Prefetch" "Prefetch"
echo.
exit /b

:c_update
echo   %_C%-- Windows Update --%_X%
<nul set /p "=  %_Y%[WORK]%_X% Stopping update services "
for %%s in (wuauserv bits cryptsvc msiserver usosvc dosvc) do net stop %%s /y >nul 2>&1
echo %_G%DONE%_X%
call :wipe "%SystemRoot%\SoftwareDistribution" "SoftwareDistribution folder"
call :wipe "%SystemRoot%\Logs\WindowsUpdate" "Windows Update logs"
del /f /q "%SystemRoot%\WindowsUpdate.log" >nul 2>&1
call :wipe "%SystemRoot%\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache" "Delivery Optimization cache"
<nul set /p "=  %_Y%[WORK]%_X% Restarting update services "
for %%s in (cryptsvc bits wuauserv msiserver) do net start %%s >nul 2>&1
echo %_G%DONE%_X%
echo.
exit /b

:c_extra
echo   %_C%-- Extra cleanup --%_X%
call :wipe "%SystemRoot%\Minidump" "Crash minidumps"
call :wipe "%ProgramData%\Microsoft\Windows\WER" "Error reporting archive"
del /f /q "%SystemRoot%\MEMORY.DMP" >nul 2>&1
del /f /s /q "%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db" >nul 2>&1
echo   %_G%[ OK ]%_X% Thumbnail cache
call :wipe "%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache" "Chrome cache"
call :wipe "%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache" "Edge cache"
powershell -nop -c "Clear-RecycleBin -Force -ErrorAction SilentlyContinue" >nul 2>&1
echo   %_G%[ OK ]%_X% Recycle Bin emptied
ipconfig /flushdns >nul 2>&1
echo   %_G%[ OK ]%_X% DNS cache flushed
call :log "Deep clean extras done"
echo.
call :ask "Also run component store cleanup with DISM, takes a few minutes?"
if errorlevel 2 exit /b
dism /online /Cleanup-Image /StartComponentCleanup
call :log "DISM component cleanup done"
exit /b

:: ---- wipe helper: %1 = folder, %2 = label
:wipe
set "tgt=%~1"
if not exist "%tgt%" goto wipe_skip
<nul set /p "=  %_Y%[WORK]%_X% %~2 "
for /l %%i in (1,1,3) do (
    <nul set /p "=."
    call :sleep 60
)
del /f /s /q "%tgt%\*" >nul 2>&1
for /d %%d in ("%tgt%\*") do rd /s /q "%%d" >nul 2>&1
echo  %_G%DONE%_X%
call :log "Cleaned: %~2"
exit /b
:wipe_skip
echo   %_D%[SKIP]%_X% %~2 %_D%- not found%_X%
exit /b

:: ---- free space helpers (MB on system drive)
:getfree
for /f %%a in ('powershell -nop -c "[math]::Round((Get-PSDrive -Name '%SystemDrive:~0,1%').Free/1MB)"') do set "%~1=%%a"
exit /b

:report
call :getfree F2
set /a FREED=F2-F1
if !FREED! lss 0 set "FREED=0"
echo   %_C%==============================================================%_X%
echo   %_W%  Space recovered : %_G%!FREED! MB%_X%
echo   %_C%==============================================================%_X%
call :log "Space recovered: !FREED! MB"
exit /b

:ask
choice /c YN /n /m "  %~1 [Y/N] : "
exit /b

:log
>>"%LOG%" echo [%date% %time%] %~1
exit /b

:: ============================================================
::                          RESET
:: ============================================================
:do_netreset
call :hdr "RESET NETWORK ADAPTER"
echo   %_D%This resets Winsock and the TCP/IP stack, and restarts adapters.%_X%
echo   %_D%You will briefly lose internet. A restart is recommended after.%_X%
call :ask "Reset network now?"
if errorlevel 2 goto menu
echo.
<nul set /p "=  %_Y%[WORK]%_X% Winsock reset "
netsh winsock reset >nul 2>&1
echo %_G%DONE%_X%
<nul set /p "=  %_Y%[WORK]%_X% TCP/IP reset "
netsh int ip reset >nul 2>&1
netsh int ipv6 reset >nul 2>&1
echo %_G%DONE%_X%
<nul set /p "=  %_Y%[WORK]%_X% Release / flush / renew "
ipconfig /release >nul 2>&1
ipconfig /flushdns >nul 2>&1
ipconfig /renew >nul 2>&1
echo %_G%DONE%_X%
<nul set /p "=  %_Y%[WORK]%_X% Restarting adapters "
powershell -nop -c "Get-NetAdapter -Physical | Where-Object {$_.Status -eq 'Up'} | Restart-NetAdapter -Confirm:$false" >nul 2>&1
echo %_G%DONE%_X%
call :log "Network reset done"
echo.
echo   %_G%Network reset complete. Please restart your PC.%_X%
goto done_pause

:do_dns
call :hdr "DNS TOOLS"
echo     %_G%[1]%_X% Flush DNS cache
echo     %_G%[2]%_X% Reset DNS to automatic (DHCP)
echo     %_G%[3]%_X% Set Google DNS      (8.8.8.8 / 8.8.4.4)
echo     %_G%[4]%_X% Set Cloudflare DNS  (1.1.1.1 / 1.0.0.1)
echo     %_G%[5]%_X% Show current DNS servers
echo     %_R%[0]%_X% Back
echo.
set "dn="
set /p "dn=  %_C%SHIV%_W% ^>^> %_X%Select: "
if "%dn%"=="1" goto dns_flush
if "%dn%"=="2" goto dns_auto
if "%dn%"=="3" goto dns_google
if "%dn%"=="4" goto dns_cf
if "%dn%"=="5" goto dns_show
goto menu

:dns_flush
ipconfig /flushdns
ipconfig /registerdns >nul 2>&1
call :log "DNS flushed"
goto done_pause

:dns_auto
powershell -nop -c "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Set-DnsClientServerAddress -ResetServerAddresses"
ipconfig /flushdns >nul 2>&1
echo   %_G%DNS reset to automatic.%_X%
call :log "DNS reset to automatic"
goto done_pause

:dns_google
powershell -nop -c "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Set-DnsClientServerAddress -ServerAddresses ('8.8.8.8','8.8.4.4')"
ipconfig /flushdns >nul 2>&1
echo   %_G%Google DNS applied.%_X%
call :log "Google DNS applied"
goto done_pause

:dns_cf
powershell -nop -c "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Set-DnsClientServerAddress -ServerAddresses ('1.1.1.1','1.0.0.1')"
ipconfig /flushdns >nul 2>&1
echo   %_G%Cloudflare DNS applied.%_X%
call :log "Cloudflare DNS applied"
goto done_pause

:dns_show
ipconfig /all | findstr /i /c:"DNS Servers" /c:"Description"
goto done_pause

:: ============================================================
::                         SECURITY
:: ============================================================
:do_mrt
call :hdr "MALICIOUS SOFTWARE REMOVAL TOOL"
if not exist "%SystemRoot%\System32\mrt.exe" goto mrt_missing
echo   %_G%Launching MRT... choose Quick, Full or Customized scan.%_X%
start "" "%SystemRoot%\System32\mrt.exe"
call :log "MRT launched"
goto done_pause
:mrt_missing
echo   %_R%mrt.exe not found on this system.%_X%
echo   %_D%MRT is delivered through Windows Update. Install pending updates, then retry.%_X%
goto done_pause

:do_defender
call :hdr "WINDOWS DEFENDER"
echo   %_D%Works only if Microsoft Defender is your active antivirus.%_X%
call :ask "Update signatures and run Quick Scan?"
if errorlevel 2 goto menu
echo.
echo   %_Y%Updating signatures...%_X%
powershell -nop -c "Update-MpSignature"
echo   %_Y%Running Quick Scan...%_X%
powershell -nop -c "Start-MpScan -ScanType QuickScan"
echo   %_G%Scan finished.%_X%
call :log "Defender update and quick scan"
goto done_pause

:: ============================================================
::                        PRO TOOLS
:: ============================================================
:do_repair
call :hdr "SYSTEM REPAIR"
echo   %_D%SFC and DISM can take 15-30 minutes. Do not close this window.%_X%
call :ask "Start repair?"
if errorlevel 2 goto menu
echo.
sfc /scannow
dism /online /cleanup-image /restorehealth
call :log "SFC and DISM repair done"
goto done_pause

:do_cleanmgr
call :hdr "WINDOWS DISK CLEANUP"
echo   %_D%A window opens: tick what you want to clean and press OK.%_X%
cleanmgr /sageset:99
cleanmgr /sagerun:99
call :log "Disk Cleanup run"
goto done_pause

:do_info
call :hdr "SYSTEM INFORMATION"
powershell -nop -c "$o=Get-CimInstance Win32_OperatingSystem; $c=Get-CimInstance Win32_Processor; $r=[math]::Round($o.TotalVisibleMemorySize/1MB,1); $f=[math]::Round($o.FreePhysicalMemory/1MB,1); Write-Host ('  OS    : '+$o.Caption+' '+$o.Version); Write-Host ('  CPU   : '+$c.Name); Write-Host ('  RAM   : '+$r+' GB total, '+$f+' GB free'); Write-Host ('  Boot  : '+$o.LastBootUpTime)"
echo.
powershell -nop -c "Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -ne $null} | Format-Table Name,@{n='Used_GB';e={[math]::Round($_.Used/1GB,1)}},@{n='Free_GB';e={[math]::Round($_.Free/1GB,1)}} -AutoSize"
goto done_pause

:do_restore
call :hdr "CREATE RESTORE POINT"
echo   %_D%Requires System Protection enabled. Windows allows one per 24 hours by default.%_X%
call :ask "Create restore point now?"
if errorlevel 2 goto menu
powershell -nop -c "Checkpoint-Computer -Description 'SHIV Cleaner' -RestorePointType MODIFY_SETTINGS"
call :log "Restore point requested"
goto done_pause

:do_log
if exist "%LOG%" (start notepad "%LOG%") else (echo   No log yet.)
goto done_pause

:: ============================================================
::                           EXIT
:: ============================================================
:do_exit
cls
call :banner_static
echo.
echo   %_G%         Thank you for using SHIV Ultimate System Cleaner%_X%
echo   %_D%                      Stay clean. Stay fast.%_X%
call :log "=== Session ended ==="
call :sleep 1500
endlocal
exit /b
