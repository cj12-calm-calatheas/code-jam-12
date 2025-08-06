#!/bin/bash

# Install Python dependencies using uv
uv venv --allow-existing
uv sync
