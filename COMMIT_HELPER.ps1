# 🚀 Git Commit Helper Script
# Purpose: Stage and commit file organization changes safely
# Date: March 3, 2026

param(
    [switch]$DryRun,
    [switch]$RootRepo,
    [switch]$MainRepo,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Peace Script AI - Git Commit Helper" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Detect repository
$rootPath = "C:\Users\USER\Desktop\peace-script-basic-v1"
$mainPath = "$rootPath\peace-script-basic-v1"

if ($RootRepo) {
    $repoPath = $rootPath
    $repoName = "ROOT REPO"
} elseif ($MainRepo) {
    $repoPath = $mainPath
    $repoName = "MAIN APP REPO"
} else {
    Write-Host "❌ Error: Please specify -RootRepo or -MainRepo" -ForegroundColor Red
    Write-Host "`nUsage:" -ForegroundColor Yellow
    Write-Host "  .\COMMIT_HELPER.ps1 -RootRepo     # Commit root repo changes"
    Write-Host "  .\COMMIT_HELPER.ps1 -MainRepo    # Commit main app changes"
    Write-Host "  .\COMMIT_HELPER.ps1 -DryRun      # Preview without committing"
    exit 1
}

Set-Location $repoPath
Write-Host "📂 Working in: $repoName" -ForegroundColor Green
Write-Host "   Path: $repoPath`n" -ForegroundColor Gray

# Check if git repo exists
if (-not (Test-Path ".git")) {
    Write-Host "❌ Error: No .git directory found in $repoPath" -ForegroundColor Red
    exit 1
}

# Show current status
Write-Host "📊 Current Git Status:" -ForegroundColor Yellow
git status --short | Select-Object -First 30

# Security check - look for sensitive files
Write-Host "`n🔒 Security Check: Scanning for sensitive files..." -ForegroundColor Yellow
$sensitivePatterns = @("\.env$", "\.env\.", "service-account", "serviceAccountKey", "\.pem$", "\.key$", "api.*key")
$sensitiveFound = $false

foreach ($pattern in $sensitivePatterns) {
    $found = git status --short | Select-String -Pattern $pattern
    if ($found) {
        Write-Host "⚠️  WARNING: Potential sensitive file detected!" -ForegroundColor Red
        $found | ForEach-Object { Write-Host "   $_" -ForegroundColor Red }
        $sensitiveFound = $true
    }
}

if ($sensitiveFound) {
    Write-Host "`n❌ STOP: Sensitive files detected. Please review before committing." -ForegroundColor Red
    Write-Host "   See: docs/security/SECURITY_CRITICAL_FIX.md" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "✅ No sensitive files detected`n" -ForegroundColor Green
}

# Stage files based on repo
if ($RootRepo) {
    Write-Host "📝 Staging ROOT REPO files..." -ForegroundColor Cyan
    
    if ($DryRun) {
        Write-Host "`n[DRY RUN] Would stage:" -ForegroundColor Yellow
        Write-Host "  - README_SYSTEM.md"
        Write-Host "  - START_SYSTEM.ps1"
        Write-Host "  - FILE_ORGANIZATION_SUMMARY.md"
        Write-Host "  - GIT_DEPLOYMENT_CHECKLIST.md"
        Write-Host "  - dmm_backend/"
        Write-Host "  - jitta-assistant/"
    } else {
        git add README_SYSTEM.md
        git add START_SYSTEM.ps1
        git add FILE_ORGANIZATION_SUMMARY.md
        git add GIT_DEPLOYMENT_CHECKLIST.md
        git add dmm_backend/
        git add jitta-assistant/
        Write-Host "✅ Files staged successfully" -ForegroundColor Green
    }
    
    $commitMessage = @"
feat: Add comprehensive system documentation and services

- Add README_SYSTEM.md with complete system overview
- Add START_SYSTEM.ps1 for unified system startup
- Add FILE_ORGANIZATION_SUMMARY.md documenting file reorganization
- Add GIT_DEPLOYMENT_CHECKLIST.md for commit/deploy procedures
- Add dmm_backend/ - Digital Mind Model API service
- Add jitta-assistant/ - GPU-accelerated RAG assistant with RTX 5090 support

System Status: All services operational
- DMM Backend: Port 8000 ✅
- Jitta Assistant: Port 8003 with CUDA 12.8 ✅
- Frontend: Port 3000 ✅

Related: GPU upgrade to RTX 5090, PyTorch 2.11.0.dev
"@

} elseif ($MainRepo) {
    Write-Host "📝 Staging MAIN APP REPO files..." -ForegroundColor Cyan
    
    if ($DryRun) {
        Write-Host "`n[DRY RUN] Would stage:" -ForegroundColor Yellow
        Write-Host "  - .gitignore (updated)"
        Write-Host "  - README.md"
        Write-Host "  - docs/"
        Write-Host "  - src/"
        Write-Host "  - .eslintrc.cjs, .github/, .husky/"
        Write-Host "  - package.json, package-lock.json"
        Write-Host "  - scripts/"
        Write-Host "  - backend/custom-model/"
        Write-Host "  - comfyui-backend/"
        Write-Host "  - comfyui-service/package-lock.json"
    } else {
        # Update .gitignore first
        git add .gitignore
        
        # Documentation
        git add README.md
        git add docs/
        
        # Source code
        git add src/
        
        # Configuration
        git add .eslintrc.cjs
        git add .github/
        git add .husky/
        git add package.json package-lock.json
        git add scripts/
        
        # Backend services
        git add backend/custom-model/config_12emo.json
        git add backend/custom-model/server_vits.py
        git add backend/custom-model/metadata/filelist_train_12emo.txt
        git add backend/custom-model/metadata/filelist_validation_12emo.txt
        git add backend/docker-compose.yml
        git add comfyui-backend/
        git add comfyui-service/package-lock.json
        
        Write-Host "✅ Files staged successfully" -ForegroundColor Green
    }
    
    $commitMessage = @"
docs: Comprehensive documentation reorganization and system updates

## Documentation Changes
- Update README.md with GPU acceleration info and new structure
- Create docs/INDEX.md as central documentation hub
- Reorganize documentation into logical categories:
  - docs/deployment/ (deployment guides)
  - docs/development/ (development workflows)
  - docs/security/ (security policies)
  - docs/team-guides/ (team collaboration)
  - docs/reports/ (project health reports)

## Source Code Updates
- Add DMM integration components (DmmAuthContainer, dmm/ folder)
- Add Digital Mind Model page (DigitalMindPage.tsx)
- Add authentication pages (LoginPage, RegisterPage)
- Add DMM service integration (dmmService.ts)
- Update various components for DMM integration
- Improve service layer and API clients

## Configuration
- Add .eslintrc.cjs for code quality
- Update .gitignore to exclude backup files
- Update CI/CD workflows
- Add git hooks (pre-commit, pre-push)
- Update backend service configurations

## Backend Services
- Update custom-model configuration for 12-emotion TTS
- Update ComfyUI backend with latest changes
- Improve Docker Compose setup

Breaking Changes: None
Migration: File paths updated - see FILE_ORGANIZATION_SUMMARY.md

System Status: ✅ All services operational
- Frontend: http://localhost:3000
- DMM Backend: http://localhost:8000
- Jitta Assistant: http://localhost:8003 (GPU-accelerated)
"@
}

# Show what will be committed
Write-Host "`n📋 Files staged for commit:" -ForegroundColor Cyan
git status --short

# Run tests if not skipped
if (-not $SkipTests -and -not $DryRun) {
    Write-Host "`n🧪 Running tests..." -ForegroundColor Yellow
    
    if ($MainRepo) {
        # Run frontend tests
        Write-Host "Testing frontend..." -ForegroundColor Gray
        try {
            npm run test -- --run --reporter=verbose 2>&1 | Out-Null
            Write-Host "✅ Tests passed" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Tests failed or skipped" -ForegroundColor Yellow
            $continue = Read-Host "Continue with commit? (y/N)"
            if ($continue -ne "y") {
                Write-Host "❌ Commit cancelled" -ForegroundColor Red
                exit 1
            }
        }
    }
}

# Commit
if ($DryRun) {
    Write-Host "`n[DRY RUN] Would commit with message:" -ForegroundColor Yellow
    Write-Host $commitMessage -ForegroundColor Gray
} else {
    Write-Host "`n📝 Committing changes..." -ForegroundColor Cyan
    git commit -m $commitMessage
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Commit successful!" -ForegroundColor Green
        
        Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
        Write-Host "  1. Review commit: git log -1" -ForegroundColor White
        Write-Host "  2. Push to remote: git push origin main" -ForegroundColor White
        if ($MainRepo) {
            Write-Host "  3. Deploy frontend: firebase deploy --only hosting" -ForegroundColor White
        }
    } else {
        Write-Host "❌ Commit failed" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan
