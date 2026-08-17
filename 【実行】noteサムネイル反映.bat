@echo off
chcp 65001 > nul
echo note サムネイルを自動反映します...
python "%~dp0update_note_thumbs.py"
echo.
pause
