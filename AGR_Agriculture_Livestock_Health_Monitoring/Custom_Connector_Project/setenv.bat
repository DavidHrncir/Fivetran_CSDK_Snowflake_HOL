@echo off

:: ============================================================================
:: Set Environment Variables in Current Shell (v3)
::
:: Description:
::   This script reads a specified environment file and sets the variables
::   in the CURRENT command prompt window.
::
::   To achieve this without requiring the user to `call` this script, it
::   dynamically generates and executes a temporary batch file containing
::   the necessary SET commands. This is the most reliable way to make
::   environment changes persist in the parent shell while correctly
::   handling values with special characters (like & or =).
::
::   NOTE: Because this script's purpose is to modify the current
::   environment, it intentionally does not use 'setlocal'.
::
:: Usage:
::   set_env.bat "C:\path\to\your\.env"
::
:: Parameters:
::   %1 - The full path to the environment file.
:: ============================================================================

:: --- Validation ---
if "%~1"=="" (
    echo.
    echo ERROR: No environment file specified.
    echo.
    echo USAGE: %~n0 "C:\path\to\your\.env"
    echo.
    exit /b 1
)

if not exist "%~1" (
    echo.
    echo ERROR: The specified file was not found.
    echo   File: "%~1"
    echo.
    exit /b 1
)

:: --- Main Processing ---

:: Define a temporary file to hold the SET commands.
:: Using %TEMP% is the standard location for temporary files in Windows.
set "TEMP_SET_SCRIPT=%TEMP%\_set_env_vars_%RANDOM%.bat"

:: Ensure the temp file is clean before we start, in the unlikely
:: event a file with the same random name exists.
if exist "%TEMP_SET_SCRIPT%" del "%TEMP_SET_SCRIPT%"

echo.
echo [+] Reading environment variables from: "%~1"
echo --------------------------------------------------

:: Loop through the input file and write "SET key=value" commands
:: to our temporary script. The quotes around "%%G=%%H" are critical
:: for handling special characters in the value.
for /f "usebackq tokens=1,* delims==" %%G in ("%~1") do (
    echo SET "%%G=%%H" >> "%TEMP_SET_SCRIPT%"
    echo Set: %%G
)

echo --------------------------------------------------
echo [+] Applying variables to the current session...

:: Execute the temporary script in the current context.
:: The 'call' command ensures the variables are set in our shell.
call "%TEMP_SET_SCRIPT%"

:: Clean up by deleting the temporary file.
del "%TEMP_SET_SCRIPT%"

echo [+] Done. Variables are now available in this terminal.
echo.
