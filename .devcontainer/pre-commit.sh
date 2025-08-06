#!/bin/bash

# Mark the current directory as safe for Git operations
git config --global --add safe.directory $PWD

# Install pre-commit hooks using uv
uv run pre-commit install
