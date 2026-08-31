@echo off
setlocal enabledelayedexpansion
docker version >NUL 2>&1
if "!ERRORLEVEL!"=="0" (
    echo Docker OK
    docker ps -a --filter name=chromadb --format {{.Names}} > "%TEMP%\chromadb_check.txt" 2>NUL
    echo --- File content ---
    type "%TEMP%\chromadb_check.txt"
    echo --- End content ---
    findstr /I "chromadb" "%TEMP%\chromadb_check.txt" >NUL
    echo Findstr ERRORLEVEL=!ERRORLEVEL!
    if "!ERRORLEVEL!"=="0" (
        echo Container FOUND
    ) else (
        echo Container NOT FOUND
    )
) else (
    echo Docker NOT running
)
pause
endlocal