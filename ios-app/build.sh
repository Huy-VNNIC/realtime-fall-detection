#!/bin/bash

# iOS App Build Script
# Tự động build và archive iOS app

set -e

echo "=================================="
echo "iOS Fall Detection App Builder"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="FallDetectionApp"
SCHEME="FallDetectionApp"
CONFIGURATION="Release"
WORKSPACE_PATH="FallDetectionApp.xcodeproj"

# Check if Xcode is installed
if ! command -v xcodebuild &> /dev/null; then
    echo -e "${RED}❌ Xcode không được cài đặt${NC}"
    echo "Vui lòng cài Xcode từ App Store"
    exit 1
fi

echo -e "${GREEN}✅ Xcode đã cài đặt${NC}"
xcodebuild -version

# Check if project exists
if [ ! -d "$WORKSPACE_PATH" ]; then
    echo -e "${RED}❌ Không tìm thấy project: $WORKSPACE_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Tìm thấy project${NC}"

# Clean build folder
echo ""
echo "🧹 Cleaning build folder..."
xcodebuild clean \
    -project "$WORKSPACE_PATH" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION"

echo -e "${GREEN}✅ Clean complete${NC}"

# Build for Simulator (Quick test)
echo ""
echo "📱 Building for Simulator..."
xcodebuild build \
    -project "$WORKSPACE_PATH" \
    -scheme "$SCHEME" \
    -configuration Debug \
    -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
    -quiet

echo -e "${GREEN}✅ Simulator build successful${NC}"

# Archive (for real device)
echo ""
echo "📦 Creating archive for real device..."
ARCHIVE_PATH="build/${PROJECT_NAME}.xcarchive"

xcodebuild archive \
    -project "$WORKSPACE_PATH" \
    -scheme "$SCHEME" \
    -configuration "$CONFIGURATION" \
    -archivePath "$ARCHIVE_PATH" \
    -quiet

if [ -d "$ARCHIVE_PATH" ]; then
    echo -e "${GREEN}✅ Archive created: $ARCHIVE_PATH${NC}"
else
    echo -e "${RED}❌ Archive failed${NC}"
    exit 1
fi

# Export IPA (requires valid signing)
echo ""
echo "📤 Exporting IPA..."
EXPORT_PATH="build/export"
EXPORT_OPTIONS="export_options.plist"

# Create export options plist if not exists
if [ ! -f "$EXPORT_OPTIONS" ]; then
    cat > "$EXPORT_OPTIONS" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>development</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
</dict>
</plist>
EOF
    echo -e "${YELLOW}⚠️  Đã tạo export_options.plist - Cần cập nhật TEAM_ID${NC}"
fi

xcodebuild -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportPath "$EXPORT_PATH" \
    -exportOptionsPlist "$EXPORT_OPTIONS" \
    -allowProvisioningUpdates \
    -quiet || true

# Summary
echo ""
echo "=================================="
echo "📊 Build Summary"
echo "=================================="
echo "✅ Project: $PROJECT_NAME"
echo "✅ Configuration: $CONFIGURATION"
if [ -d "$EXPORT_PATH" ]; then
    echo "✅ IPA Location: $EXPORT_PATH"
fi
echo ""
echo -e "${GREEN}✨ Build completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Open Xcode and select your device"
echo "2. Press Play (⌘R) to install on device"
echo "3. Or distribute IPA for ad-hoc installation"
