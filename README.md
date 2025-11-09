# go to your venv bin folder (adjust path if needed)
cd /Users/xiang/github/mouse_auto/.venv/bin

# create a minimal Info.plist (overwrites if exists — safe to inspect first)
cat > Info.plist <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>rumps</string>
</dict>
</plist>
EOF

# verify
plutil -p Info.plist
