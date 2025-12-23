#!/bin/bash

set -e

module="patterns_book/"
tests="tests/"
BLUE=$(tput setaf 4)
RESET=$(tput sgr0)

echo "${BLUE}Running ruff...${RESET}"
ruff format $module $tests
ruff check $module $tests --fix

echo
echo "${BLUE}Running mypy...${RESET}"
mypy $module $tests --strict
