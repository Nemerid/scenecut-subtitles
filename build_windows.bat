@echo off
REM ─────────────────────────────────────────────────────────────────────────────
REM  build_windows.bat — Construit Scene Cut Subtitles.exe
REM  Usage : double-cliquer ou lancer depuis un terminal Windows
REM  Resultat : dist\Scene_Cut_Subtitles_Windows.zip
REM ─────────────────────────────────────────────────────────────────────────────

cd /d "%~dp0"
echo ================================================
echo   Build - Scene Cut Subtitles (Windows)
echo ================================================

echo [1/4] Verification Python...
python --version
if errorlevel 1 (
    echo ERREUR : Python n'est pas installe ou pas dans le PATH.
    echo Telecharger Python sur https://python.org
    pause
    exit /b 1
)

echo [2/4] Installation des dependances...
pip install --quiet --upgrade pyinstaller websockets aiohttp

echo [3/4] PyInstaller...
pyinstaller scenecut_subtitles.spec --clean --noconfirm

echo [4/4] Creation de l'archive...
cd dist
powershell -Command "Compress-Archive -Path 'Scene Cut Subtitles.exe' -DestinationPath 'Scene_Cut_Subtitles_Windows.zip' -Force"
cd ..

echo.
echo   Build termine !
echo   Fichier : dist\Scene_Cut_Subtitles_Windows.zip
echo.
pause
