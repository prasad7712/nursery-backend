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
echo "Step 1.5: Checking environment variables"
echo "DATABASE_URL is set: $([ -n "$DATABASE_URL" ] && echo "YES" || echo "NO - THIS IS CRITICAL!")"
echo "ENVIRONMENT is: ${ENVIRONMENT:-not set}"

echo ""
echo "Step 2: Upgrading pip, setuptools, and wheel"
pip install --upgrade pip setuptools wheel

echo ""
echo "Step 3: Installing dependencies"
pip install --prefer-binary --no-build-isolation -r requirements.txt

echo ""
echo "✅ Build completed successfully"

# Set environment variable for Prisma to find binaries
export PRISMA_PYTHON_BINARIES_CACHE=/opt/render/.cache/prisma-python
echo "✅ Binary cache set to: $PRISMA_PYTHON_BINARIES_CACHE"

echo ""
echo "Step 8: Verifying Prisma setup"
python -c "import prisma; print('✅ Prisma client loaded successfully')"

echo ""
echo "======================================"
echo "✅ Build completed successfully"
echo "======================================"
