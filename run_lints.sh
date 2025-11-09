#!/bin/bash

set -e

module="patterns_book/"
BLUE=$(tput setaf 4)
RESET=$(tput sgr0)

echo "${BLUE}Running ruff...${RESET}"
ruff format $module
ruff check $module --fix

echo
echo "${BLUE}Running mypy...${RESET}"
mypy $module --strict
