%CM_PYTHON_BIN_WITH_PATH% -m pip install torch%CM_TMP_PIP_VERSION_STRING%
IF %ERRORLEVEL% NEQ 0 EXIT 1

