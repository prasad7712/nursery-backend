#!/bin/bash
# Render build script for nursery-backend
# Force Python 3.11 and use only pre-built wheels

set -e

echo "==> Python version:"
python --version

echo "==> Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "==> Installing dependencies with wheel preference..."
pip install --prefer-binary \
    --only-binary :all: \
    --no-build-isolation \
    -r requirements.txt

echo "==> Build completed successfully!"
