#!/bin/bash

# Script to create a macOS desktop app for Able2

echo "🖥️  Creating Able2 Desktop App..."

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create the app bundle directory structure
APP_NAME="Able2.app"
DESKTOP_PATH="$SCRIPT_DIR/$APP_NAME"
CONTENTS_PATH="$DESKTOP_PATH/Contents"
MACOS_PATH="$CONTENTS_PATH/MacOS"
RESOURCES_PATH="$CONTENTS_PATH/Resources"

echo "📁 Creating app bundle structure..."

# Remove existing app if it exists
if [ -d "$DESKTOP_PATH" ]; then
    rm -rf "$DESKTOP_PATH"
fi

mkdir -p "$MACOS_PATH"
mkdir -p "$RESOURCES_PATH"

# Create the executable script
cat > "$MACOS_PATH/Able2" << EOF
#!/bin/bash

# Able2 Desktop App Launcher
# This script launches Able2 from the desktop app

# Get the path to the Able2 directory
ABLE2_BASE_PATH="/Users/will/Able_2.1"
LAUNCHER_PATH="\$ABLE2_BASE_PATH/launch_able2.sh"

# Check if the launcher exists
if [ ! -f "\$LAUNCHER_PATH" ]; then
    osascript << 'OSASCRIPT'
display dialog "Able2 launcher not found at expected location. Please make sure Able2 is installed in /Users/will/Able_2/" with title "Able2 Error" buttons {"OK"} default button "OK"
OSASCRIPT
    exit 1
fi

# Open Terminal and run the launcher
osascript << OSASCRIPT
tell application "Terminal"
    activate
    do script "cd '\$ABLE2_BASE_PATH' && ./launch_able2.sh"
end tell
OSASCRIPT

EOF

# Make the executable script runnable
chmod +x "$MACOS_PATH/Able2"

# Create Info.plist
cat > "$CONTENTS_PATH/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Able2</string>
    <key>CFBundleIconFile</key>
    <string>app_icon</string>
    <key>CFBundleIdentifier</key>
    <string>com.able2.research-assistant</string>
    <key>CFBundleName</key>
    <string>Able2</string>
    <key>CFBundleDisplayName</key>
    <string>Able2 PDF Research Assistant</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>ABLE</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOF

# Create a simple text-based icon representation
# (In a real production app, you'd want a proper .icns file)
echo "Creating app icon placeholder..."
touch "$RESOURCES_PATH/app_icon.icns"

echo "✅ Desktop app created successfully!"
echo ""
echo "🎉 Able2.app has been created in /Users/will/Able_2.1/!"
echo ""
echo "📝 To use:"
echo "   1. Double-click Able2.app in /Users/will/Able_2.1/"
echo "   2. Terminal will open and start the Able2 servers"
echo "   3. Your browser will automatically open to the application"
echo ""
echo "💡 Alternative ways to start Able2:"
echo "   • Run './launch_able2.sh' from /Users/will/Able_2.1/"
echo "   • Run './start_able2.sh' from /Users/will/Able_2.1/able2/"
echo ""
echo "🔧 Note: The first time you run the app, macOS may ask for permission."
echo "    If prompted, go to System Preferences > Security & Privacy and allow the app to run."
echo ""
echo "🌟 The app is now ready to use!"