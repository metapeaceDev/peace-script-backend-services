#!/bin/bash
# Fix Virtual Environment for Phase 2 Authentication
# This script recreates the venv with correct paths

set -e  # Exit on error

echo "🔧 Fixing Virtual Environment for Authentication System"
echo "======================================================"
echo

# Define paths
BACKEND_DIR="/Users/surasak.peace/Desktop/peace script model v1.4/dmm_backend"
OLD_VENV="$BACKEND_DIR/venv"
BACKUP_VENV="$BACKEND_DIR/venv_old_$(date +%Y%m%d_%H%M%S)"

cd "$BACKEND_DIR"

# Step 1: Backup old venv
echo "📦 Step 1: Backing up old venv..."
if [ -d "$OLD_VENV" ]; then
    mv "$OLD_VENV" "$BACKUP_VENV"
    echo "   ✅ Backed up to: $BACKUP_VENV"
else
    echo "   ⚠️  No existing venv found"
fi
echo

# Step 2: Create new venv
echo "🐍 Step 2: Creating new virtual environment..."
python3.9 -m venv venv
echo "   ✅ New venv created"
echo

# Step 3: Upgrade pip
echo "📦 Step 3: Upgrading pip..."
./venv/bin/pip install --upgrade pip -q
echo "   ✅ Pip upgraded"
echo

# Step 4: Install dependencies
echo "📚 Step 4: Installing all dependencies..."
echo "   This may take a minute..."
./venv/bin/pip install -r requirements.txt -q
echo "   ✅ Dependencies installed"
echo

# Step 5: Verify auth packages
echo "🔍 Step 5: Verifying authentication packages..."
JOSE_CHECK=$(./venv/bin/pip list | grep python-jose || echo "")
PASSLIB_CHECK=$(./venv/bin/pip list | grep passlib || echo "")

if [ -n "$JOSE_CHECK" ] && [ -n "$PASSLIB_CHECK" ]; then
    echo "   ✅ python-jose: installed"
    echo "   ✅ passlib: installed"
else
    echo "   ⚠️  Installing auth packages manually..."
    ./venv/bin/pip install 'python-jose[cryptography]' 'passlib[bcrypt]' python-multipart -q
    echo "   ✅ Auth packages installed"
fi
echo

# Step 6: Test imports
echo "🧪 Step 6: Testing imports..."
TEST_RESULT=$(./venv/bin/python -c "
try:
    from routers.auth_router import router
    from routers.simulation_router import router as sim_router
    print('SUCCESS')
except Exception as e:
    print(f'FAILED: {e}')
" 2>&1)

if [[ "$TEST_RESULT" == *"SUCCESS"* ]]; then
    echo "   ✅ Auth router imports successfully"
    echo "   ✅ Simulation router imports successfully"
else
    echo "   ❌ Import test failed:"
    echo "   $TEST_RESULT"
    echo
    echo "⚠️  Please check the error above"
    exit 1
fi
echo

# Step 7: Summary
echo "✅ Virtual Environment Fixed Successfully!"
echo "==========================================="
echo
echo "📊 Summary:"
echo "   • Old venv backed up to: $(basename $BACKUP_VENV)"
echo "   • New venv created with Python 3.9"
echo "   • All dependencies installed"
echo "   • Auth router ready to use"
echo
echo "🚀 Next Steps:"
echo "   1. Restart backend:"
echo "      ./venv/bin/uvicorn main:app --reload"
echo
echo "   2. Test auth endpoints:"
echo "      curl http://127.0.0.1:8000/api/auth/health"
echo
echo "   3. View API docs:"
echo "      open http://127.0.0.1:8000/docs"
echo
echo "   4. Run test script:"
echo "      ./venv/bin/pip install requests -q"
echo "      ./venv/bin/python test_auth_api.py"
echo

# Cleanup old backup if very old (optional)
OLD_BACKUPS=$(find "$BACKEND_DIR" -name "venv_old_*" -type d -mtime +7 2>/dev/null | wc -l)
if [ $OLD_BACKUPS -gt 0 ]; then
    echo "💡 Tip: Found $OLD_BACKUPS old venv backups (>7 days old)"
    echo "    You can remove them with:"
    echo "    find \"$BACKEND_DIR\" -name \"venv_old_*\" -type d -mtime +7 -exec rm -rf {} +"
    echo
fi

echo "🎉 Phase 2 Authentication is ready to test!"
