<#
    update_bank_local.ps1 — refresh your PRIVATE bank values locally.

    Runs scripts/update_bank.py to rebuild data/bank.json from your local
    data/bank.txt (RuneLite Bank Export) + live GE prices. Nothing here is ever
    committed or published — the bank stays local-only.

    One-time scheduling (runs daily at 6am). Paste into PowerShell, adjusting
    the path if your repo lives elsewhere:

        $script = "$HOME\OneDrive\Documents\GitHub\osrs-ironman-progession-tracker\scripts\update_bank_local.ps1"
        Register-ScheduledTask -TaskName "OSRS Bank Update" `
            -Trigger (New-ScheduledTaskTrigger -Daily -At 6am) `
            -Action  (New-ScheduledTaskAction -Execute "powershell.exe" `
                        -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`"")

    Remove it later with:  Unregister-ScheduledTask -TaskName "OSRS Bank Update"
#>
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot

# Find a Python interpreter (python.exe or the py launcher)
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
if (-not $py) {
    Write-Error "Python 3 was not found on PATH. Install it from python.org to refresh bank values."
    exit 1
}

Write-Host "Refreshing private bank values from data/bank.txt ..."
& $py.Source (Join-Path $repo "scripts\update_bank.py")
Write-Host "Done. Open index.html locally to view the Bank tab."
