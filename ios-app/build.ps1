# PowerShell Build Script for iOS Development on Windows
# This script helps setup and manage iOS development from Windows

Write-Host "================================" -ForegroundColor Cyan
Write-Host "iOS App Development Helper" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if running on Windows
if ($env:OS -ne "Windows_NT") {
    Write-Host "❌ This script is for Windows only" -ForegroundColor Red
    Write-Host "For Mac, use build.sh instead" -ForegroundColor Yellow
    exit 1
}

Write-Host "ℹ️  iOS development requires a Mac with Xcode" -ForegroundColor Yellow
Write-Host ""

# Options
Write-Host "Available options:" -ForegroundColor Green
Write-Host "1. Check project structure"
Write-Host "2. Generate Xcode project file info"
Write-Host "3. Start backend server"
Write-Host "4. Test WebSocket connection"
Write-Host "5. Show IP addresses"
Write-Host "6. Open documentation"
Write-Host ""

$choice = Read-Host "Select an option (1-6)"

switch ($choice) {
    "1" {
        Write-Host "`n📁 Project Structure:" -ForegroundColor Green
        Get-ChildItem -Path "FallDetectionApp" -Recurse -Include "*.swift" | 
            Select-Object FullName | 
            ForEach-Object { $_.FullName.Replace($PWD, ".") }
    }
    
    "2" {
        Write-Host "`n📄 Xcode Project Info:" -ForegroundColor Green
        if (Test-Path "FallDetectionApp.xcodeproj") {
            Write-Host "✅ Project file exists" -ForegroundColor Green
            Write-Host "Location: $PWD\FallDetectionApp.xcodeproj" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "To open on Mac:" -ForegroundColor Yellow
            Write-Host "  cd ios-app" -ForegroundColor Gray
            Write-Host "  open FallDetectionApp.xcodeproj" -ForegroundColor Gray
        } else {
            Write-Host "❌ Project file not found" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host "`n🚀 Starting Backend Server..." -ForegroundColor Green
        Set-Location ..
        python main.py
    }
    
    "4" {
        Write-Host "`n🔌 Testing WebSocket..." -ForegroundColor Green
        $wsTest = @"
<!DOCTYPE html>
<html>
<head><title>WebSocket Test</title></head>
<body>
    <h1>WebSocket Test</h1>
    <div id="status" style="color:red">Disconnected</div>
    <div id="messages" style="margin-top:20px"></div>
    <script>
        const ws = new WebSocket('ws://localhost:8080');
        ws.onopen = () => {
            document.getElementById('status').textContent = 'Connected';
            document.getElementById('status').style.color = 'green';
        };
        ws.onmessage = (event) => {
            const div = document.createElement('div');
            div.textContent = new Date().toLocaleTimeString() + ': ' + event.data;
            document.getElementById('messages').appendChild(div);
        };
        ws.onerror = (error) => {
            document.getElementById('status').textContent = 'Error: ' + error;
            document.getElementById('status').style.color = 'red';
        };
    </script>
</body>
</html>
"@
        $wsTest | Out-File -FilePath "test_ws.html" -Encoding UTF8
        Write-Host "✅ Created test_ws.html" -ForegroundColor Green
        Write-Host "Opening in browser..." -ForegroundColor Cyan
        Start-Process "test_ws.html"
    }
    
    "5" {
        Write-Host "`n🌐 Network Information:" -ForegroundColor Green
        Write-Host ""
        Write-Host "Local IP Addresses:" -ForegroundColor Cyan
        Get-NetIPAddress -AddressFamily IPv4 | 
            Where-Object { $_.IPAddress -ne "127.0.0.1" } |
            Select-Object IPAddress, InterfaceAlias |
            Format-Table -AutoSize
        
        Write-Host "Use one of these IP addresses in iOS app settings" -ForegroundColor Yellow
        Write-Host "Example: 192.168.1.100:8080" -ForegroundColor Gray
    }
    
    "6" {
        Write-Host "`n📖 Opening Documentation..." -ForegroundColor Green
        if (Test-Path "README.md") {
            Start-Process "README.md"
        }
        if (Test-Path "QUICKSTART.md") {
            Start-Process "QUICKSTART.md"
        }
    }
    
    default {
        Write-Host "❌ Invalid option" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "For full iOS development:" -ForegroundColor Yellow
Write-Host "1. Transfer project folder to Mac" -ForegroundColor Gray
Write-Host "2. Open FallDetectionApp.xcodeproj in Xcode" -ForegroundColor Gray
Write-Host "3. Connect iPhone or use Simulator" -ForegroundColor Gray
Write-Host "4. Press Run (⌘R)" -ForegroundColor Gray
Write-Host "================================" -ForegroundColor Cyan
