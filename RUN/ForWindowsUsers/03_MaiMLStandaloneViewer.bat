@echo off
setlocal
cd /d "%~dp0"

REM HTML File path
set "HTML_FILE=..\..\SRC\03_MaiMLStandaloneViewer\HTML-MaiMLViewer.html"

REM Open the HTML file using the default web browser
start "" "%HTML_FILE%"