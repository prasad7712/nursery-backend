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
echo "Step 4: Generating Prisma client"
python -m prisma generate

echo ""
echo "Step 5: Setting up Prisma cache directory"
export PRISMA_PYTHON_BINARIES_CACHE=/opt/render/.cache/prisma-python
mkdir -p $PRISMA_PYTHON_BINARIES_CACHE
echo "Cache directory: $PRISMA_PYTHON_BINARIES_CACHE"

echo ""
echo "Step 6: Fetching Prisma query engine binaries"
python -m prisma py fetch

echo ""
echo "Step 6: Fetching Prisma query engine binaries"
python -m prisma py fetch

echo ""
echo "Step 7: Setting up Prisma binary permissions"
# Make all Prisma binaries executable
find /opt/render/.cache/prisma-python -name "prisma-query-engine*" -type f 2>/dev/null | while read binary; do
  chmod +x "$binary"
  echo "✅ Made executable: $(basename $binary)"
done

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
