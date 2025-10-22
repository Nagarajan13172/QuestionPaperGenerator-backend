#!/bin/bash
# Quick verification script

echo "=================================="
echo "🔍 SYLLABUS VISIBILITY FIX - VERIFICATION"
echo "=================================="
echo ""

# Check if storage directory exists
echo "1. Checking storage directory..."
if [ -d "storage" ]; then
    echo "   ✓ storage/ directory exists"
    ls -lh storage/
else
    echo "   ⚠ storage/ directory not found (will be created on first run)"
fi
echo ""

# Check if static files exist
echo "2. Checking static files..."
if [ -f "static/test_ui.html" ]; then
    echo "   ✓ Test UI available at: http://localhost:8000/static/test_ui.html"
else
    echo "   ✗ Test UI not found"
fi
echo ""

# Check if server is running
echo "3. Checking if server is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ Server is running"
    echo ""
    echo "   Health check response:"
    curl -s http://localhost:8000/health | python3 -m json.tool
    echo ""
else
    echo "   ⚠ Server is not running"
    echo "   Start it with: python -m uvicorn app.main:app --reload"
fi
echo ""

# Check API endpoints
echo "4. Checking syllabi endpoint..."
if curl -s http://localhost:8000/api/syllabus/ > /dev/null 2>&1; then
    SYLLABI_COUNT=$(curl -s http://localhost:8000/api/syllabus/ | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))")
    echo "   ✓ API is responding"
    echo "   📚 Found $SYLLABI_COUNT syllabi"
    echo ""
    
    if [ "$SYLLABI_COUNT" -gt "0" ]; then
        echo "   Sample syllabus:"
        curl -s http://localhost:8000/api/syllabus/ | python3 -m json.tool | head -30
    else
        echo "   ⚠ No syllabi found. Try one of:"
        echo "     - Upload via test UI: http://localhost:8000/static/test_ui.html"
        echo "     - Run migration: python migrate_storage.py"
        echo "     - Use test script: python test_api.py"
    fi
else
    echo "   ✗ API not responding (server may not be running)"
fi
echo ""

echo "=================================="
echo "✅ VERIFICATION COMPLETE"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Start/restart server: python -m uvicorn app.main:app --reload"
echo "  2. Open test UI: http://localhost:8000/static/test_ui.html"
echo "  3. Or use API docs: http://localhost:8000/api/docs"
echo ""
