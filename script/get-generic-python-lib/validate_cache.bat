IF NOT DEFINED MLC_TMP_CURRENT_SCRIPT_PATH SET MLC_TMP_CURRENT_SCRIPT_PATH=%CD%

%MLC_PYTHON_BIN_WITH_PATH% %MLC_TMP_CURRENT_SCRIPT_PATH%\detect-version.py
IF %ERRORLEVEL% NEQ 0 EXIT 1
