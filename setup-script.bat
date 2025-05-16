@echo off
:: Setup script for ScholarSynthesis (Windows version)

echo Checking Python version...
python -c "import sys; version=sys.version_info; exit(1) if version.major < 3 or (version.major == 3 and version.minor < 8) else exit(0)"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python 3.8 or higher is required.
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv litreview_env

:: Activate virtual environment
call litreview_env\Scripts\activate.bat

:: Install required packages
echo Installing required packages...
pip install --upgrade pip
pip install -e .

:: Create directories
echo Creating directories...
if not exist output mkdir output
if not exist .cache mkdir .cache

echo.
echo Setup complete!
echo.
echo To use ScholarSynthesis:
echo 1. Activate the virtual environment:
echo    litreview_env\Scripts\activate.bat
echo.
echo 2. Run the agent with your paper details:
echo    litreview-agent --title "Your Paper Title" --abstract "Your paper abstract" --num_papers 15
echo.
echo 3. For more options:
echo    litreview-agent --help

pause 