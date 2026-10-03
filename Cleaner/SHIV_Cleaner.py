#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  SHIV ULTIMATE SYSTEM CLEANER  v2.0   (Python edition, standard library only)
  Clean | Reset | Security | Pro Tools
  Works on Windows 10 / 11.  Run it normally - it asks for Administrator
  rights by itself (UAC).
==============================================================================
"""
import os
import sys

if os.name != "nt":
    print("SHIV Cleaner works on Windows only.")
    sys.exit(1)

import ctypes
import datetime
import glob
import msvcrt
import shutil
import stat
import subprocess
import time

APP_NAME = "SHIV Ultimate System Cleaner"
VERSION = "2.0"

FROZEN = bool(getattr(sys, "frozen", False)) or ("__compiled__" in globals())
SCRIPT_PATH = os.path.abspath(sys.executable if FROZEN else __file__)
BASE_DIR = os.path.dirname(SCRIPT_PATH)
LOG_FILE = os.path.join(BASE_DIR, "SHIV_Cleaner_Log.txt")

SYSROOT = os.environ.get("SystemRoot", r"C:\Windows")
SYSDRIVE = os.environ.get("SystemDrive", "C:")
LOCALAPPDATA = os.environ.get("LOCALAPPDATA", "")
APPDATA = os.environ.get("APPDATA", "")
PROGRAMDATA = os.environ.get("ProgramData", r"C:\ProgramData")
USER_TEMP = os.environ.get("TEMP", "")

STATS = {"bytes": 0}

# ----------------------------------------------------------------------------
#  Colours / ANSI
# ----------------------------------------------------------------------------
ESC = "\x1b"
R = ESC + "[91m"
G = ESC + "[92m"
Y = ESC + "[93m"
B = ESC + "[94m"
M = ESC + "[95m"
C = ESC + "[96m"
W = ESC + "[97m"
D = ESC + "[90m"
X = ESC + "[0m"


def c256(n):
    return "%s[38;5;%dm" % (ESC, n)


def enable_ansi():
    try:
        k = ctypes.windll.kernel32
        k.SetConsoleOutputCP(65001)
        k.SetConsoleCP(65001)
        h = k.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if k.GetConsoleMode(h, ctypes.byref(mode)):
            k.SetConsoleMode(h, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        k.SetConsoleTitleW("SHIV - Ultimate System Cleaner")
    except Exception:
        pass
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    os.system("mode con: cols=100 lines=50 >nul 2>&1")


def out(text=""):
    sys.stdout.write(text)
    sys.stdout.flush()


def cls():
    os.system("cls")


def hide_cursor():
    out(ESC + "[?25l")


def show_cursor():
    out(ESC + "[?25h")


# ----------------------------------------------------------------------------
#  Admin / system helpers
# ----------------------------------------------------------------------------
def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def elevate():
    """Relaunch this program with UAC 'Run as administrator'."""
    try:
        if FROZEN:
            exe = sys.executable
            params = " ".join('"%s"' % a for a in sys.argv[1:])
        else:
            exe = sys.executable
            params = " ".join('"%s"' % a for a in [SCRIPT_PATH] + sys.argv[1:])
        return ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1) > 32
    except Exception:
        return False


def sysexe(name):
    """Full path in System32 (uses Sysnative if a 32-bit Python runs on 64-bit Windows)."""
    folder = "Sysnative" if os.environ.get("PROCESSOR_ARCHITEW6432") else "System32"
    p = os.path.join(SYSROOT, folder, name)
    return p if os.path.exists(p) else name


POWERSHELL = sysexe(os.path.join("WindowsPowerShell", "v1.0", "powershell.exe"))
NO_WINDOW = 0x08000000


def run_quiet(args):
    try:
        return subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              stdin=subprocess.DEVNULL, creationflags=NO_WINDOW).returncode
    except Exception:
        return -1


def run_live(args):
    try:
        return subprocess.call(args)
    except Exception as e:
        print("  %sCould not run %s: %s%s" % (R, args[0], e, X))
        return -1


def ps(command, live=False):
    args = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command]
    return run_live(args) if live else run_quiet(args)


def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("[%s] %s\n" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
    except OSError:
        pass


def free_bytes():
    try:
        return shutil.disk_usage(SYSDRIVE + "\\").free
    except Exception:
        return 0


def fmt(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return ("%d %s" % (n, unit)) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0


# ----------------------------------------------------------------------------
#  Cleaning engine
# ----------------------------------------------------------------------------
def _norm(p):
    return os.path.normcase(os.path.abspath(p))


def _build_protect():
    paths = {_norm(SCRIPT_PATH), _norm(LOG_FILE), _norm(BASE_DIR)}
    mp = getattr(sys, "_MEIPASS", None)  # PyInstaller one-file extraction folder
    if mp:
        paths.add(_norm(mp))
    try:
        paths.add(_norm(os.path.dirname(os.path.abspath(__file__))))
    except Exception:
        pass
    return paths


PROTECT = _build_protect()


def is_protected(path):
    """Never delete the running program (or a folder that contains it)."""
    ep = _norm(path)
    for pp in PROTECT:
        if pp == ep or pp.startswith(ep + os.sep):
            return True
    return False


def folder_size(path):
    total = 0
    for root, _dirs, files in os.walk(path, onerror=lambda e: None):
        for name in files:
            try:
                total += os.lstat(os.path.join(root, name)).st_size
            except OSError:
                pass
    return total


def _rm_error(func, path, *_):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def _rmtree(path):
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=_rm_error)
    else:
        shutil.rmtree(path, onerror=_rm_error)


def clear_folder(path):
    """Delete everything inside `path` (not the folder itself). Locked files are skipped."""
    try:
        entries = list(os.scandir(path))
    except OSError:
        return
    for entry in entries:
        if is_protected(entry.path):
            continue
        try:
            if entry.is_dir(follow_symlinks=False):
                _rmtree(entry.path)
            else:
                try:
                    os.remove(entry.path)
                except PermissionError:
                    os.chmod(entry.path, stat.S_IWRITE)
                    os.remove(entry.path)
        except Exception:
            pass


def working(label):
    out("  %s[WORK]%s %s " % (Y, X, label))


def dots(n=3, delay=0.06):
    for _ in range(n):
        out(".")
        time.sleep(delay)


def wipe(path, label, quiet_skip=False):
    """Clean one folder with a status line."""
    if not path or not os.path.isdir(path):
        if not quiet_skip:
            print("  %s[SKIP]%s %s %s- not found%s" % (D, X, label, D, X))
        return 0
    if len(os.path.splitdrive(path)[1].strip("\\/")) == 0:   # never wipe a drive root
        print("  %s[SKIP]%s %s %s- unsafe path%s" % (D, X, label, D, X))
        return 0
    before = folder_size(path)
    working(label)
    dots()
    clear_folder(path)
    freed = max(before - folder_size(path), 0)
    STATS["bytes"] += freed
    print(" %sDONE%s %s(%s)%s" % (G, X, D, fmt(freed), X))
    log("Cleaned: %s (%s)" % (label, fmt(freed)))
    return freed


def delete_glob(pattern, label):
    working(label)
    dots()
    freed = 0
    for f in glob.glob(pattern):
        try:
            if is_protected(f):
                continue
            size = os.lstat(f).st_size
            try:
                os.remove(f)
            except PermissionError:
                os.chmod(f, stat.S_IWRITE)
                os.remove(f)
            freed += size
        except Exception:
            pass
    STATS["bytes"] += freed
    print(" %sDONE%s %s(%s)%s" % (G, X, D, fmt(freed), X))
    log("Cleaned: %s (%s)" % (label, fmt(freed)))


def services(names, action):
    for s in names:
        args = [sysexe("net.exe"), action, s]
        if action == "stop":
            args.append("/y")
        run_quiet(args)


UPDATE_STOP = ["wuauserv", "bits", "cryptsvc", "msiserver", "usosvc", "dosvc"]
UPDATE_START = ["cryptsvc", "bits", "wuauserv", "msiserver"]


# ----------------------------------------------------------------------------
#  Banner (big rainbow SHIV)
# ----------------------------------------------------------------------------
BLOCK = "\u2588"
PAL = [196, 202, 208, 214, 220, 226, 190, 154, 118, 82, 46, 48, 51, 45, 39,
       33, 27, 57, 93, 129, 165, 201, 199]
GLYPHS = {
    "S": [" #### ", "#     ", " ###  ", "    # ", "####  "],
    "H": ["#   # ", "#   # ", "##### ", "#   # ", "#   # "],
    "I": ["##### ", "  #   ", "  #   ", "  #   ", "##### "],
    "V": ["#   # ", "#   # ", "#   # ", " # #  ", "  #   "],
}
WORD = "SHIV"
IND = " " * 26


def _big(seg):
    return "".join((BLOCK if ch == "#" else " ") * 2 for ch in seg)


SEGS = {k: [_big(s) for s in rows] for k, rows in GLYPHS.items()}


def banner_lines(frame):
    lines = []
    for r in range(5):
        parts = []
        for k, ch in enumerate(WORD):
            parts.append(c256(PAL[(frame + r * 2 + k * 6) % len(PAL)]) + SEGS[ch][r])
        line = IND + "".join(parts) + X
        lines.append(line)
        lines.append(line)
    return lines


def banner_static():
    print()
    print("\n".join(banner_lines(10)))


def typewriter(text, delay=0.018):
    for ch in text:
        out(ch)
        time.sleep(delay)


def progress(label, width=24):
    out(IND + W + label)
    for i in range(1, width + 1):
        out("%s%s" % (c256(20 + i * 8), BLOCK))
        time.sleep(0.025)
    print("%s done" % X)


def intro():
    cls()
    hide_cursor()
    print()
    for f in range(36):
        out("%s[2;1H%s\n" % (ESC, "\n".join(banner_lines(f))))
        time.sleep(0.03)
    print()
    out(IND + C)
    typewriter("U L T I M A T E   S Y S T E M   C L E A N E R")
    print(X)
    print()
    progress("Loading modules   ")
    time.sleep(0.5)
    show_cursor()


def header(title):
    cls()
    banner_static()
    print("  %s  S H I V   U L T I M A T E   C L E A N E R%s" % (M, X))
    print("  %s  %s%s" % (D, "-" * 60, X))
    print("  %s  %s%s" % (Y, title, X))
    print()


def sub(title):
    print("  %s-- %s --%s" % (C, title, X))


def ask(question):
    out("  %s [Y/N] : " % question)
    while True:
        ch = msvcrt.getwch()
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch.lower() in ("y", "n"):
            print(ch.upper())
            return ch.lower() == "y"


def pause():
    print()
    out("  %sPress any key to return to the menu...%s" % (D, X))
    msvcrt.getwch()


def begin():
    STATS["bytes"] = 0
    return free_bytes()


def report(start_free):
    gained = max(free_bytes() - start_free, 0)
    print()
    print("  %s%s%s" % (C, "=" * 62, X))
    print("  %s  Files removed      : %s%s%s" % (W, G, fmt(STATS["bytes"]), X))
    print("  %s  Free space gained  : %s%s%s" % (W, G, fmt(gained), X))
    print("  %s  Free on %s        : %s%s%s" % (W, SYSDRIVE, G, fmt(free_bytes()), X))
    print("  %s%s%s" % (C, "=" * 62, X))
    log("Report: removed %s, free space gained %s" % (fmt(STATS["bytes"]), fmt(gained)))


# ----------------------------------------------------------------------------
#  CLEAN
# ----------------------------------------------------------------------------
def c_quick():
    sub("Temp / %TEMP% / Recent / Prefetch")
    wipe(os.path.join(SYSROOT, "Temp"), "Windows Temp folder")
    wipe(USER_TEMP, "User %TEMP% folder")
    wipe(os.path.join(APPDATA, "Microsoft", "Windows", "Recent"), "Recent files and jump lists")
    wipe(os.path.join(SYSROOT, "Prefetch"), "Prefetch")
    print()


def c_update():
    sub("Windows Update")
    working("Stopping update services")
    services(UPDATE_STOP, "stop")
    print("%sDONE%s" % (G, X))
    wipe(os.path.join(SYSROOT, "SoftwareDistribution"), "SoftwareDistribution folder")
    wipe(os.path.join(SYSROOT, "Logs", "WindowsUpdate"), "Windows Update logs")
    delete_glob(os.path.join(SYSROOT, "WindowsUpdate.log"), "WindowsUpdate.log")
    wipe(os.path.join(SYSROOT, "ServiceProfiles", "NetworkService", "AppData", "Local",
                      "Microsoft", "Windows", "DeliveryOptimization", "Cache"),
         "Delivery Optimization cache")
    working("Restarting update services")
    services(UPDATE_START, "start")
    print("%sDONE%s" % (G, X))
    print()


def c_extra():
    sub("Extra cleanup")
    wipe(os.path.join(SYSROOT, "Minidump"), "Crash minidumps")
    wipe(os.path.join(PROGRAMDATA, "Microsoft", "Windows", "WER"), "Error reporting archive")
    delete_glob(os.path.join(SYSROOT, "MEMORY.DMP"), "Memory dump")
    delete_glob(os.path.join(LOCALAPPDATA, "Microsoft", "Windows", "Explorer", "thumbcache_*.db"),
                "Thumbnail cache")

    browsers = {
        "Chrome": ["Google", "Chrome"],
        "Edge": ["Microsoft", "Edge"],
        "Brave": ["BraveSoftware", "Brave-Browser"],
    }
    for name, parts in browsers.items():
        user_data = os.path.join(LOCALAPPDATA, *parts, "User Data")
        profiles = glob.glob(os.path.join(user_data, "Default")) + glob.glob(os.path.join(user_data, "Profile *"))
        for prof in profiles:
            for cache in ("Cache", "Code Cache", "GPUCache"):
                wipe(os.path.join(prof, cache), "%s %s %s" % (name, os.path.basename(prof), cache),
                     quiet_skip=True)
    for cache2 in glob.glob(os.path.join(LOCALAPPDATA, "Mozilla", "Firefox", "Profiles", "*", "cache2")):
        wipe(cache2, "Firefox cache")

    working("Emptying Recycle Bin")
    ps("Clear-RecycleBin -Force -ErrorAction SilentlyContinue")
    print("%sDONE%s" % (G, X))
    log("Recycle Bin emptied")

    working("Flushing DNS cache")
    run_quiet([sysexe("ipconfig.exe"), "/flushdns"])
    print("%sDONE%s" % (G, X))
    log("DNS cache flushed")
    print()

    if ask("Also run component store cleanup with DISM (takes a few minutes)?"):
        print()
        run_live([sysexe("dism.exe"), "/online", "/Cleanup-Image", "/StartComponentCleanup"])
        log("DISM component cleanup done")


def do_quick():
    header("QUICK CLEAN")
    start = begin()
    c_quick()
    report(start)
    pause()


def do_update():
    header("WINDOWS UPDATE CLEAN")
    print("  %sNote: update history resets after clearing SoftwareDistribution.%s" % (D, X))
    if not ask("Continue?"):
        return
    print()
    start = begin()
    c_update()
    report(start)
    pause()


def do_deep():
    header("DEEP CLEAN")
    print("  %sTip: close your browsers first for best results.%s" % (D, X))
    if not ask("Start deep clean?"):
        return
    print()
    start = begin()
    c_quick()
    c_update()
    c_extra()
    report(start)
    pause()


# ----------------------------------------------------------------------------
#  RESET (optional)
# ----------------------------------------------------------------------------
def do_netreset():
    header("RESET NETWORK ADAPTER")
    print("  %sThis resets Winsock and the TCP/IP stack, and restarts adapters.%s" % (D, X))
    print("  %sYou will briefly lose internet. A restart is recommended after.%s" % (D, X))
    if not ask("Reset network now?"):
        return
    print()
    netsh = sysexe("netsh.exe")
    ipc = sysexe("ipconfig.exe")

    working("Winsock reset")
    run_quiet([netsh, "winsock", "reset"])
    print("%sDONE%s" % (G, X))

    working("TCP/IP reset")
    run_quiet([netsh, "int", "ip", "reset"])
    run_quiet([netsh, "int", "ipv6", "reset"])
    print("%sDONE%s" % (G, X))

    working("Release / flush / renew")
    run_quiet([ipc, "/release"])
    run_quiet([ipc, "/flushdns"])
    run_quiet([ipc, "/renew"])
    print("%sDONE%s" % (G, X))

    working("Restarting adapters")
    ps("Get-NetAdapter -Physical | Where-Object {$_.Status -eq 'Up'} | Restart-NetAdapter -Confirm:$false")
    print("%sDONE%s" % (G, X))

    log("Network reset done")
    print()
    print("  %sNetwork reset complete. Please restart your PC.%s" % (G, X))
    pause()


UP_ADAPTERS = "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | "


def do_dns():
    header("DNS TOOLS")
    print("    %s[1]%s Flush DNS cache" % (G, X))
    print("    %s[2]%s Reset DNS to automatic (DHCP)" % (G, X))
    print("    %s[3]%s Set Google DNS      (8.8.8.8 / 8.8.4.4)" % (G, X))
    print("    %s[4]%s Set Cloudflare DNS  (1.1.1.1 / 1.0.0.1)" % (G, X))
    print("    %s[5]%s Show current DNS servers" % (G, X))
    print("    %s[0]%s Back" % (R, X))
    print()
    choice = input("  %sSHIV%s >> %sSelect: " % (C, W, X)).strip()
    print()
    ipc = sysexe("ipconfig.exe")
    if choice == "1":
        run_live([ipc, "/flushdns"])
        run_quiet([ipc, "/registerdns"])
        log("DNS flushed")
    elif choice == "2":
        ps(UP_ADAPTERS + "Set-DnsClientServerAddress -ResetServerAddresses")
        run_quiet([ipc, "/flushdns"])
        print("  %sDNS reset to automatic.%s" % (G, X))
        log("DNS reset to automatic")
    elif choice == "3":
        ps(UP_ADAPTERS + "Set-DnsClientServerAddress -ServerAddresses ('8.8.8.8','8.8.4.4')")
        run_quiet([ipc, "/flushdns"])
        print("  %sGoogle DNS applied.%s" % (G, X))
        log("Google DNS applied")
    elif choice == "4":
        ps(UP_ADAPTERS + "Set-DnsClientServerAddress -ServerAddresses ('1.1.1.1','1.0.0.1')")
        run_quiet([ipc, "/flushdns"])
        print("  %sCloudflare DNS applied.%s" % (G, X))
        log("Cloudflare DNS applied")
    elif choice == "5":
        ps("Get-DnsClientServerAddress -AddressFamily IPv4 | "
           "Format-Table InterfaceAlias,ServerAddresses -AutoSize", live=True)
    else:
        return
    pause()


# ----------------------------------------------------------------------------
#  SECURITY
# ----------------------------------------------------------------------------
def do_mrt():
    header("MALICIOUS SOFTWARE REMOVAL TOOL")
    mrt = sysexe("mrt.exe")
    if os.path.isabs(mrt) and os.path.exists(mrt):
        print("  %sLaunching MRT... choose Quick, Full or Customized scan.%s" % (G, X))
        try:
            subprocess.Popen([mrt])
            log("MRT launched")
        except Exception as e:
            print("  %sCould not start MRT: %s%s" % (R, e, X))
    else:
        print("  %smrt.exe not found on this system.%s" % (R, X))
        print("  %sMRT is delivered through Windows Update. Install pending updates, then retry.%s" % (D, X))
    pause()


def do_defender():
    header("WINDOWS DEFENDER")
    print("  %sWorks only if Microsoft Defender is your active antivirus.%s" % (D, X))
    if not ask("Update signatures and run Quick Scan?"):
        return
    print()
    print("  %sUpdating signatures...%s" % (Y, X))
    ps("Update-MpSignature", live=True)
    print("  %sRunning Quick Scan...%s" % (Y, X))
    ps("Start-MpScan -ScanType QuickScan", live=True)
    print("  %sScan finished.%s" % (G, X))
    log("Defender update and quick scan")
    pause()


# ----------------------------------------------------------------------------
#  PRO TOOLS
# ----------------------------------------------------------------------------
def do_repair():
    header("SYSTEM REPAIR")
    print("  %sSFC and DISM can take 15-30 minutes. Do not close this window.%s" % (D, X))
    if not ask("Start repair?"):
        return
    print()
    run_live([sysexe("sfc.exe"), "/scannow"])
    run_live([sysexe("dism.exe"), "/online", "/cleanup-image", "/restorehealth"])
    log("SFC and DISM repair done")
    pause()


def do_cleanmgr():
    header("WINDOWS DISK CLEANUP")
    print("  %sA window opens: tick what you want to clean and press OK.%s" % (D, X))
    cm = sysexe("cleanmgr.exe")
    run_live([cm, "/sageset:99"])
    run_live([cm, "/sagerun:99"])
    log("Disk Cleanup run")
    pause()


INFO_PS = (
    "$o=Get-CimInstance Win32_OperatingSystem; $c=Get-CimInstance Win32_Processor; "
    "$r=[math]::Round($o.TotalVisibleMemorySize/1MB,1); $f=[math]::Round($o.FreePhysicalMemory/1MB,1); "
    "Write-Host ('  OS    : '+$o.Caption+' '+$o.Version); "
    "Write-Host ('  CPU   : '+$c.Name); "
    "Write-Host ('  RAM   : '+$r+' GB total, '+$f+' GB free'); "
    "Write-Host ('  Boot  : '+$o.LastBootUpTime)"
)
DISKS_PS = (
    "Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -ne $null} | "
    "Format-Table Name,@{n='Used_GB';e={[math]::Round($_.Used/1GB,1)}},"
    "@{n='Free_GB';e={[math]::Round($_.Free/1GB,1)}} -AutoSize"
)


def do_info():
    header("SYSTEM INFORMATION")
    ps(INFO_PS, live=True)
    print()
    ps(DISKS_PS, live=True)
    pause()


def do_restore():
    header("CREATE RESTORE POINT")
    print("  %sRequires System Protection enabled. Windows allows one per 24 hours by default.%s" % (D, X))
    if not ask("Create restore point now?"):
        return
    print()
    ps("Checkpoint-Computer -Description 'SHIV Cleaner' -RestorePointType MODIFY_SETTINGS", live=True)
    log("Restore point requested")
    pause()


def do_log():
    header("VIEW LOG")
    if os.path.exists(LOG_FILE):
        try:
            subprocess.Popen(["notepad.exe", LOG_FILE])
        except Exception as e:
            print("  %sCould not open log: %s%s" % (R, e, X))
    else:
        print("  No log yet.")
    pause()


# ----------------------------------------------------------------------------
#  MENU
# ----------------------------------------------------------------------------
def print_menu():
    cls()
    banner_static()
    line = "  %s  %s%s" % (C, "=" * 78, X)
    print("  %s         U L T I M A T E   S Y S T E M   C L E A N E R   %sv%s%s" % (M, D, VERSION, X))
    print(line)
    print("  %s  CLEAN%s" % (Y, X))
    print("    %s[1]%s Quick Clean         %sTemp, %%TEMP%%, Recent, Prefetch%s" % (G, X, D, X))
    print("    %s[2]%s Windows Update      %sUpdate logs, SoftwareDistribution folder%s" % (G, X, D, X))
    print("    %s[3]%s Deep Clean          %s1 + 2 + Recycle Bin, Thumbnails, Browser cache, Dumps%s" % (G, X, D, X))
    print("  %s  RESET  %s(optional)%s" % (Y, D, X))
    print("    %s[4]%s Network Adapter     %sWinsock, TCP/IP stack, restart adapters%s" % (G, X, D, X))
    print("    %s[5]%s DNS Tools           %sFlush, reset to auto, Google DNS, Cloudflare DNS%s" % (G, X, D, X))
    print("  %s  SECURITY%s" % (Y, X))
    print("    %s[6]%s MRT Tool            %sMicrosoft Malicious Software Removal Tool%s" % (G, X, D, X))
    print("    %s[7]%s Defender            %sUpdate signatures + Quick Scan%s" % (G, X, D, X))
    print("  %s  PRO TOOLS%s" % (Y, X))
    print("    %s[8]%s System Repair       %sSFC /scannow + DISM RestoreHealth%s" % (G, X, D, X))
    print("    %s[9]%s Disk Cleanup        %sWindows cleanmgr with your selection%s" % (G, X, D, X))
    print("    %s[A]%s System Information  %sOS, CPU, RAM, disks%s" % (G, X, D, X))
    print("    %s[B]%s Restore Point       %sCreate a safety restore point%s" % (G, X, D, X))
    print("    %s[C]%s View Log            %sOpen SHIV_Cleaner_Log.txt%s" % (G, X, D, X))
    print("    %s[0]%s Exit" % (R, X))
    print(line)
    print()


ACTIONS = {
    "1": do_quick, "2": do_update, "3": do_deep,
    "4": do_netreset, "5": do_dns,
    "6": do_mrt, "7": do_defender,
    "8": do_repair, "9": do_cleanmgr,
    "A": do_info, "B": do_restore, "C": do_log,
}


def goodbye():
    cls()
    banner_static()
    print()
    print("  %s         Thank you for using SHIV Ultimate System Cleaner%s" % (G, X))
    print("  %s                      Stay clean. Stay fast.%s" % (D, X))
    log("=== Session ended ===")
    time.sleep(1.5)


def main():
    enable_ansi()
    if not is_admin():
        print("Requesting Administrator rights...")
        if elevate():
            return
        print("Administrator rights are required. Right-click and choose 'Run as administrator'.")
        input("Press Enter to close...")
        return

    log("=== Session started ===")
    try:
        intro()
        while True:
            print_menu()
            try:
                choice = input("  %sSHIV%s >> %sSelect option: " % (C, W, X)).strip().upper()
            except EOFError:
                break
            if choice == "0":
                break
            action = ACTIONS.get(choice)
            if not action:
                continue
            try:
                action()
            except KeyboardInterrupt:
                print("\n  %sCancelled.%s" % (Y, X))
                pause()
            except Exception as e:  # keep the menu alive whatever happens
                print("\n  %sUnexpected error: %s%s" % (R, e, X))
                log("ERROR: %s" % e)
                pause()
    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        goodbye()


if __name__ == "__main__":
    main()
