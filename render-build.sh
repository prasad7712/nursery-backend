#!/bin/bash
# Render deployment build script
set -e

echo "======================================"
echo "🔧 Starting Render Build Process"
echo "======================================"

echo ""
echo "Step 1: Python version check"
python --version

echo ""
echo "Step 2: Upgrading pip, setuptools, and wheel"
pip install --upgrade pip setuptools wheel

echo ""
echo "Step 3: Installing dependencies"
pip install --prefer-binary --no-build-isolation -r requirements.txt

echo ""
echo "Step 4: Generating Prisma client"
python -m prisma generate

echo ""
echo "Step 5: Fetching Prisma query engine binaries"
export PRISMA_PYTHON_BINARIES_CACHE=/opt/render/.prisma-cache
mkdir -p $PRISMA_PYTHON_BINARIES_CACHE
python -m prisma py fetch --target debian-openssl-3.0 || python -m prisma py fetch

echo ""
echo "Step 6: Verifying Prisma setup"
python -c "import prisma; print('✅ Prisma client loaded successfully')"

echo ""
echo "======================================"
echo "✅ Build completed successfully"
echo "======================================"
