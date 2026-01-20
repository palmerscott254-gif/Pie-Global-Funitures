#!/bin/bash
# Media Management Checklist
# Use this after making changes in Django Admin

echo "📋 Media Management Checklist"
echo "====================================="
echo ""

# Check if we're in the backend directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Run this from the backend directory (where manage.py is)"
    exit 1
fi

echo "1️⃣  Check for S3 credentials..."
python check_env.py
echo ""

echo "2️⃣  Deduplicating media records (dry run)..."
python manage.py deduplicate_media --dry-run
echo ""

echo "3️⃣  Exporting current media to JSON..."
python export_media_records.py
echo ""

echo "4️⃣  Ready to commit?"
echo "   $ git add backend/"
echo "   $ git commit -m 'Update: Media sync after admin changes'"
echo "   $ git push"
echo ""

echo "✅ Checklist complete!"
echo ""
echo "📖 For detailed info, see: MEDIA_SYNC_GUIDE.md"
