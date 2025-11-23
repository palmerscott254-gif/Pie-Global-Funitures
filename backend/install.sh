#!/bin/bash
# Automated installation script for Linux/macOS
# Pie Global Furniture Backend Setup

set -e  # Exit on error

echo "============================================================"
echo "  Pie Global Furniture Backend Installation"
echo "============================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11+ and try again"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Step 1: Upgrade pip, setuptools, and wheel
echo "============================================================"
echo "Step 1: Upgrading pip, setuptools, and wheel..."
echo "============================================================"
python3 -m pip install --upgrade pip setuptools>=65.0.0 wheel>=0.38.0
echo ""

# Step 2: Install dependencies
echo "============================================================"
echo "Step 2: Installing project dependencies..."
echo "============================================================"
pip3 install -r requirements.txt
echo ""

echo "============================================================"
echo "  Installation Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure your settings"
echo "  2. Run: python3 manage.py migrate"
echo "  3. Run: python3 manage.py createsuperuser"
echo "  4. Run: python3 manage.py runserver"
echo ""
