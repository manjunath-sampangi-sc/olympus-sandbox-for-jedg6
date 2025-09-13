#!/bin/bash

echo "🔍 DBT Installation Troubleshooting Script for macOS"
echo "=================================================="

# Check Python version
echo "1. Checking Python version..."
python3 --version
echo ""

# Check pip version
echo "2. Checking pip3 version..."
pip3 --version
echo ""

# Check current PATH
echo "3. Current PATH:"
echo $PATH
echo ""

# Check if dbt is installed via brew
echo "4. Checking brew installations..."
brew list | grep dbt || echo "No dbt found in brew"
echo ""

# Check if dbt is available in different locations
echo "5. Searching for dbt in common locations..."
which dbt 2>/dev/null || echo "dbt not found in PATH"
ls -la /usr/local/bin/dbt 2>/dev/null || echo "dbt not in /usr/local/bin/"
ls -la /opt/homebrew/bin/dbt 2>/dev/null || echo "dbt not in /opt/homebrew/bin/"
ls -la ~/.local/bin/dbt 2>/dev/null || echo "dbt not in ~/.local/bin/"
echo ""

# Check virtual environment
echo "6. Checking virtual environment..."
if [ -d "streamlit_app/venv" ]; then
    echo "Virtual environment found at streamlit_app/venv"
    echo "Activating virtual environment and checking dbt..."
    cd streamlit_app
    source venv/bin/activate
    which dbt 2>/dev/null || echo "dbt not found in virtual environment"
    pip3 list | grep dbt || echo "dbt not installed in virtual environment"
    cd ..
else
    echo "Virtual environment not found at streamlit_app/venv"
fi
echo ""

echo "🛠️  RECOMMENDED SOLUTIONS:"
echo "========================="
echo ""
echo "Solution 1: Install dbt in virtual environment (RECOMMENDED)"
echo "cd streamlit_app"
echo "source venv/bin/activate"
echo "pip3 install dbt-snowflake"
echo "dbt --version"
echo ""
echo "Solution 2: If brew installed dbt, add to PATH"
echo "echo 'export PATH=\"/opt/homebrew/bin:\$PATH\"' >> ~/.zshrc"
echo "source ~/.zshrc"
echo ""
echo "Solution 3: Install dbt globally with pip3"
echo "pip3 install --user dbt-snowflake"
echo "echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc"
echo "source ~/.zshrc"
echo ""
echo "Solution 4: Uninstall and reinstall"
echo "brew uninstall dbt"
echo "pip3 uninstall dbt-core dbt-snowflake"
echo "pip3 install dbt-snowflake"