#!/bin/bash
# Render build script for nursery-backend
# This handles installation of packages with pre-built wheels to avoid compilation

set -e

echo "==> Setting up build environment..."
python --version
pip --version

echo "==> Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "==> Installing Python dependencies..."
# Install with specific options to use pre-built wheels and handle Rust packages
pip install --prefer-binary \
    --only-binary :all: \
    -r requirements.txt

echo "==> Generating Prisma client..."
python -m prisma generate

echo "==> Build completed successfully!"
