@echo off
set "OUTPUT=full_script_pp.txt"

:: Очистка выходного файла
type nul > "%OUTPUT%" 2>nul

:: Рекурсивный поиск .py файлов, исключая папку venv
for /f "delims=" %%F in ('dir /s /b *.py ^| findstr /v /i "\venv\\"') do (
    echo === %%F === >> "%OUTPUT%"
    type "%%F" >> "%OUTPUT%"
    echo. >> "%OUTPUT%"
)

echo Готово! Все .py файлы (кроме тех, что внутри venv) объединены в "%OUTPUT%"
pause