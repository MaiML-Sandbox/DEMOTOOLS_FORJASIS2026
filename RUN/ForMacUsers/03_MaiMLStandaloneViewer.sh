#!/bin/bash
set -e
cd "$(dirname "$0")"

# HTML File path
HTML_FILE="../../SRC/03_MaiMLStandaloneViewer/HTML-MaiMLViewer.html"

# Open the HTML file using the default web browser
open "$HTML_FILE"