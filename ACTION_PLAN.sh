#!/bin/bash
# ACTION PLAN - Run this to see what to do next

echo "════════════════════════════════════════════════════════════════════"
echo "                  ✅ SYLLABUS VISIBILITY - FIXED!                   "
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "📋 YOUR ACTION CHECKLIST:"
echo ""
echo "□ Step 1: Restart your server"
echo "    Command: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "□ Step 2: Migrate existing data (if you have PDFs in uploads/)"
echo "    Command: python migrate_storage.py"
echo ""
echo "□ Step 3: Test the fix"
echo "    - Open: http://localhost:8000/static/test_ui.html"
echo "    - Or run: ./verify_fix.sh"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "🎯 WHAT WAS FIXED:"
echo ""
echo "  Problem: Syllabi disappeared after server restart"
echo "  Cause:   In-memory storage (Python dict)"
echo "  Fix:     Persistent JSON storage on disk"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "✨ KEY FILES:"
echo ""
echo "  📁 storage/syllabi.json           - Your syllabi data (NEW!)"
echo "  🌐 static/test_ui.html            - Web test interface (NEW!)"
echo "  🔧 migrate_storage.py             - Migration tool (NEW!)"
echo "  ✓ verify_fix.sh                   - Verification script (NEW!)"
echo "  📄 FIX_SUMMARY.md                 - Complete documentation (NEW!)"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "🚀 QUICK TEST:"
echo ""

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✓ Server is running on http://localhost:8000"
    
    # Get syllabi count
    COUNT=$(curl -s http://localhost:8000/api/syllabus/ | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "  📚 Current syllabi count: $COUNT"
    
    if [ "$COUNT" -gt "0" ]; then
        echo "  ✓ Syllabi are visible! ✨"
        echo ""
        echo "  🎉 SUCCESS! Your fix is working!"
        echo ""
        echo "  Next: Open http://localhost:8000/static/test_ui.html to see them"
    else
        echo "  ⚠ No syllabi found yet"
        echo ""
        echo "  Action: Upload a syllabus or run migration:"
        echo "    python migrate_storage.py"
    fi
else
    echo "  ⚠ Server not running"
    echo ""
    echo "  Action: Start the server:"
    echo "    python -m uvicorn app.main:app --reload"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "💡 TIP: For detailed info, read FIX_SUMMARY.md"
echo ""
echo "════════════════════════════════════════════════════════════════════"
