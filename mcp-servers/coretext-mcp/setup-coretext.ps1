# PowerShell script to set up CoreText MCP Server on Windows
# Run this script as: .\setup-coretext.ps1

Write-Host "🚀 Setting up CoreText MCP Server..." -ForegroundColor Cyan
Write-Host ""

# Define paths
$sourcePath = Get-Location
$targetPath = "C:\github\coretext-mcp"

# Create target directory
Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
New-Item -ItemType Directory -Path "$targetPath\src" -Force | Out-Null
New-Item -ItemType Directory -Path "$targetPath\data" -Force | Out-Null

# Copy files
Write-Host "📄 Copying files..." -ForegroundColor Yellow
$files = @(
    "package.json",
    "README.md",
    ".env.example",
    ".gitignore",
    "Dockerfile",
    ".dockerignore",
    "claude_desktop_config.json",
    "TEACHING_GUIDE.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $targetPath -Force
        Write-Host "   ✓ $file" -ForegroundColor Green
    }
}

# Copy source files
if (Test-Path "src\index.js") {
    Copy-Item "src\index.js" -Destination "$targetPath\src" -Force
    Write-Host "   ✓ src\index.js" -ForegroundColor Green
}

# Copy data files
if (Test-Path "data\memory.json") {
    Copy-Item "data\memory.json" -Destination "$targetPath\data" -Force
    Write-Host "   ✓ data\memory.json" -ForegroundColor Green
}

Write-Host ""
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
Set-Location $targetPath
npm install

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Next steps:" -ForegroundColor Cyan
Write-Host "1. cd $targetPath" -ForegroundColor White
Write-Host "2. Copy .env.example to .env and add your Deepseek API key (optional)" -ForegroundColor White
Write-Host "3. npm run inspector" -ForegroundColor White
Write-Host ""
Write-Host "🎓 Teaching guide available at: $targetPath\TEACHING_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "Good luck with your O'Reilly session, Tim! 🚀" -ForegroundColor Magenta
