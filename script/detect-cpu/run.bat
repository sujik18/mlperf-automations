rem systeminfo /fo csv > tmp-systeminfo.csv
@echo off
REM Try PowerShell first
powershell -Command "Get-CimInstance Win32_Processor | Export-Csv -Path tmp-wmic-cpu.csv -NoTypeInformation" 2>nul
if %errorlevel% neq 0 (
    REM Fallback for old Windows with WMIC
    wmic cpu get /FORMAT:csv > tmp-wmic-cpu.csv
)

