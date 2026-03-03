# 📋 Git & Deployment Checklist

**Date:** March 3, 2026  
**Purpose:** Verify correctness of files for Git commit, ignore, and deployment

---

## 🎯 Repository Structure Analysis

### **Git Repositories Found:**

```
Desktop/peace-script-basic-v1/          [✅ ROOT REPO]
├── .git/                               (Root monorepo)
├── dmm_backend/                        (No .git - part of root)
├── jitta-assistant/                    (No .git - part of root)
└── peace-script-basic-v1/              [✅ MAIN APP REPO]
    └── .git/                           (Frontend app repo)
```

**Key Insight:**
- **2 separate Git repositories**
- Root repo manages: Backend services (DMM, Jitta)
- Main app repo manages: Frontend React application

---

## ✅ FILES TO COMMIT

### **ROOT REPO** (`Desktop/peace-script-basic-v1/`)

**Status:** Currently showing as untracked (`??`)

#### **New Files (Should Commit):**
```
✅ README_SYSTEM.md                     # Complete system documentation
✅ START_SYSTEM.ps1                     # System startup script
✅ FILE_ORGANIZATION_SUMMARY.md         # Organization report
```

#### **Folders (Should Commit):**
```
✅ dmm_backend/                         # DMM Backend service
   ├── main.py
   ├── requirements.txt
   ├── routers/
   ├── core/
   └── tests/

✅ jitta-assistant/                     # Jitta AI Assistant (GPU)
   ├── server.py
   ├── requirements.txt
   ├── app/
   ├── tests/
   └── GPU_UPGRADE_REPORT.md
```

**EXCLUDE from commit:**
- `dmm_backend/.env`
- `jitta-assistant/.env`
- `jitta-assistant/data/` (ChromaDB database)
- `.venv/` (Python virtual environment)
- `logs/` (runtime logs)

---

### **MAIN APP REPO** (`peace-script-basic-v1/peace-script-basic-v1/`)

#### **Documentation (Should Commit):**
```
✅ README.md                           # Updated with GPU info
✅ docs/INDEX.md                       # NEW: Documentation hub
✅ docs/deployment/                    # Moved deployment docs
   ├── DEPLOYMENT_STATUS.md
   ├── GIT_DEPLOYMENT_GUIDE.md
   └── FIREBASE_UNIFIED_DEPLOYMENT_PLAN.md
✅ docs/development/                   # Moved development docs
   ├── FILE_MANAGEMENT_CHECKLIST.md
   ├── FILE_MANAGEMENT_GUIDE.md
   ├── PROJECT_INTEGRATION_PLAN.md
   ├── INTEGRATION_SUMMARY.md
   ├── INTEGRATION_PLAN.md
   ├── INTEGRATION_COMPLETION_SUMMARY.md
   └── RELEASE_FILE_ORGANIZATION.md
✅ docs/security/                      # NEW: Security docs
   ├── SECURITY_CRITICAL_FIX.md
   └── URGENT_API_KEY_ROTATION.md
✅ docs/team-guides/                   # NEW: Team guides
   ├── HOW_TO_SHARE_KEYS.md
   └── TEAM_ENV_SHARING_GUIDE.md
✅ docs/reports/PROJECT_HEALTH_REPORT.md
```

#### **Source Code Changes (Should Commit):**
```
✅ src/App.tsx                         # Modified
✅ src/components/Step5Output.tsx      # Modified
✅ src/components/Studio.tsx           # Modified
✅ src/components/UsageDashboard.tsx   # Modified
✅ src/components/timeline/MultiTrackTimeline.tsx
✅ src/services/*.ts                   # Various service updates
✅ src/test/App.test.tsx               # Updated tests

✅ NEW Components:
   ├── src/components/DmmAuthContainer.tsx
   ├── src/components/dmm/
   ├── src/pages/DigitalMindPage.tsx
   ├── src/pages/LoginPage.tsx
   ├── src/pages/RegisterPage.tsx
   └── src/services/dmmService.ts
```

#### **Configuration Changes (Should Commit):**
```
✅ .eslintrc.cjs                       # Added
✅ .github/workflows/ci.yml            # Modified
✅ .husky/pre-commit                   # Modified
✅ .husky/pre-push                     # Added
✅ package.json                        # Modified
✅ package-lock.json                   # Modified
✅ scripts/validate-env.js             # Modified
```

#### **Backend Services (Should Commit):**
```
✅ backend/custom-model/config_12emo.json
✅ backend/custom-model/server_vits.py
✅ backend/custom-model/metadata/filelist_*.txt (main files only)
✅ backend/docker-compose.yml
✅ comfyui-backend/main.py
✅ comfyui-backend/requirements.txt
✅ comfyui-service/package-lock.json
```

#### **Deleted Files (Already Staged as Deleted):**
```
✅ D FILE_MANAGEMENT_CHECKLIST.md      # Moved to docs/development/
✅ D FILE_MANAGEMENT_GUIDE.md          # Moved to docs/development/
✅ D FIREBASE_UNIFIED_DEPLOYMENT_PLAN.md
✅ D HOW_TO_SHARE_KEYS.md
✅ D INTEGRATION_SUMMARY.md
✅ D PROJECT_HEALTH_REPORT.md
✅ D PROJECT_INTEGRATION_PLAN.md
✅ D RELEASE_FILE_ORGANIZATION.md
✅ D TEAM_ENV_SHARING_GUIDE.md
✅ D URGENT_API_KEY_ROTATION.md
✅ D extract-keys-simple.ps1           # Moved to archive/
✅ D extract-team-keys.ps1
✅ D prepare-keys-for-team.ps1
✅ D rotate-and-deploy.ps1
✅ D setup-team-env.ps1
```

---

## ⛔ FILES TO ADD TO .GITIGNORE

### **Main App Repo - Add These Rules:**

```gitignore
# Backup and temporary metadata files
backend/custom-model/metadata/*.bak.*
backend/custom-model/metadata/*.bad.*
backend/custom-model/metadata/*_balanced.txt

# Backup tools (if not needed in repo)
tools/validate_character_keys.cjs
tools/validate_character_keys.js

# Archive folder with old scripts
archive/
```

### **Recommended .gitignore Update:**

Add to `peace-script-basic-v1/.gitignore` after line 150:

```gitignore
# Metadata backup files (generated during training)
backend/custom-model/metadata/*.bak.*
backend/custom-model/metadata/*.bad.*
backend/custom-model/metadata/*_balanced.txt
backend/custom-model/tools/

# Archived scripts (superseded by START_SYSTEM.ps1)
archive/scripts/

# Validation tools (duplicates)
tools/validate_character_keys.cjs
```

---

## 🚀 FILES TO DEPLOY

### **Frontend (Firebase Hosting)**

**Deploy These:**
```
✅ dist/                               # Build output (npm run build)
✅ firebase.json                       # Firebase config
✅ firestore.rules                     # Firestore security rules
✅ firestore.indexes.json              # Database indexes
✅ storage.rules                       # Storage security rules
✅ .firebaserc                         # Firebase project config
```

**DO NOT deploy:**
```
❌ .env, .env.local, .env.production   # Contains API keys
❌ service-account-key.json            # Firebase admin credentials
❌ node_modules/                       # Dependencies (too large)
❌ src/ (source code)                  # Only deploy built dist/
❌ tests/                              # Test files
❌ docs/                               # Documentation (not needed in production)
```

**Deployment Command:**
```bash
cd peace-script-basic-v1
npm run build              # Build production bundle
firebase deploy --only hosting
```

---

### **DMM Backend (Production Server)**

**Deploy These:**
```
✅ dmm_backend/main.py
✅ dmm_backend/routers/
✅ dmm_backend/core/
✅ dmm_backend/requirements.txt
✅ dmm_backend/tests/
```

**DO NOT deploy:**
```
❌ dmm_backend/.env                    # Use server environment variables
❌ dmm_backend/__pycache__/            # Python cache
❌ dmm_backend/.pytest_cache/          # Test cache
```

**Deployment Method:**
- Docker container (recommended)
- Or direct uvicorn deployment
- Environment variables set on server (not from .env file)

**Setup Commands:**
```bash
# On production server
cd dmm_backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### **Jitta Assistant (Production Server)**

**Deploy These:**
```
✅ jitta-assistant/server.py
✅ jitta-assistant/app/
✅ jitta-assistant/requirements.txt
✅ jitta-assistant/tests/
✅ jitta-assistant/GPU_UPGRADE_REPORT.md (for reference)
```

**DO NOT deploy:**
```
❌ jitta-assistant/.env                # Use server environment variables
❌ jitta-assistant/data/               # ChromaDB - re-ingest on server
❌ jitta-assistant/__pycache__/
❌ jitta-assistant/.pytest_cache/
❌ jitta-assistant/.venv/              # Create fresh venv on server
```

**Deployment Requirements:**
- Server with NVIDIA GPU (RTX 5090 or compatible)
- CUDA 12.8 installed
- PyTorch 2.11.0.dev or later (with sm_120 support)

**Setup Commands:**
```bash
# On production server with GPU
cd jitta-assistant
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Run ingest to populate ChromaDB
python -m uvicorn server:app --host 0.0.0.0 --port 8003
```

---

## 📝 GIT COMMIT RECOMMENDATIONS

### **ROOT REPO - Commit Structure**

```bash
cd C:\Users\USER\Desktop\peace-script-basic-v1

# 1. Stage new documentation
git add README_SYSTEM.md
git add START_SYSTEM.ps1
git add FILE_ORGANIZATION_SUMMARY.md

# 2. Stage DMM Backend
git add dmm_backend/

# 3. Stage Jitta Assistant
git add jitta-assistant/

# 4. Commit
git commit -m "feat: Add comprehensive system documentation and services

- Add README_SYSTEM.md with complete system overview
- Add START_SYSTEM.ps1 for unified system startup
- Add FILE_ORGANIZATION_SUMMARY.md documenting file reorganization
- Add dmm_backend/ - Digital Mind Model API service
- Add jitta-assistant/ - GPU-accelerated RAG assistant with RTX 5090 support

System Status: All services operational
- DMM Backend: Port 8000 ✅
- Jitta Assistant: Port 8003 with CUDA 12.8 ✅
- Frontend: Port 3000 ✅

Related: GPU upgrade to RTX 5090, PyTorch 2.11.0.dev"
```

---

### **MAIN APP REPO - Commit Structure**

```bash
cd C:\Users\USER\Desktop\peace-script-basic-v1\peace-script-basic-v1

# 1. Update .gitignore first
# (Add rules for backup files - see section above)
git add .gitignore

# 2. Stage documentation changes
git add README.md
git add docs/

# 3. Stage source code changes
git add src/

# 4. Stage configuration changes
git add .eslintrc.cjs .github/ .husky/
git add package.json package-lock.json
git add scripts/

# 5. Stage backend changes
git add backend/custom-model/config_12emo.json
git add backend/custom-model/server_vits.py
git add backend/custom-model/metadata/filelist_train_12emo.txt
git add backend/custom-model/metadata/filelist_validation_12emo.txt
git add backend/docker-compose.yml
git add comfyui-backend/
git add comfyui-service/package-lock.json

# 6. Review what will be committed
git status

# 7. Commit
git commit -m "docs: Comprehensive documentation reorganization and system updates

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

Closes #N/A"
```

---

## ⚠️ PRE-COMMIT CHECKLIST

### **Before Committing:**

- [ ] **Check for secrets:** No API keys, passwords, or tokens in code
- [ ] **Verify .gitignore:** All sensitive files excluded
- [ ] **Remove backup files:** No .bak, .bad, .tmp files staged
- [ ] **Test locally:** System starts with `START_SYSTEM.ps1`
- [ ] **Run tests:** `npm run test` passes
- [ ] **Build succeeds:** `npm run build` completes without errors
- [ ] **Linting passes:** `npm run lint` shows no errors
- [ ] **Review diff:** `git diff --cached` shows expected changes only

### **Sensitive Files Check:**

```bash
# Verify no secrets are staged
git diff --cached | grep -E "(API_KEY|SECRET|PASSWORD|TOKEN)" || echo "✅ No secrets found"

# Verify .env files not staged
git status | grep "\.env" && echo "⚠️  WARNING: .env file detected!" || echo "✅ No .env files staged"
```

---

## 🔒 SECURITY CRITICAL - DO NOT COMMIT

**NEVER commit these files:**

```
❌ .env
❌ .env.local
❌ .env.production
❌ service-account-key.json
❌ firebase-adminsdk-*.json
❌ **/serviceAccountKey.json
❌ *.key
❌ *.pem
❌ *.p12
❌ team-api-keys_*.txt
❌ Any file with API keys or secrets
```

**If accidentally committed:**
1. **Rotate all exposed keys immediately**
2. Use `git filter-branch` or BFG Repo-Cleaner to remove from history
3. Force push to remote (coordinate with team)
4. See: `docs/security/URGENT_API_KEY_ROTATION.md`

---

## 📊 DEPLOYMENT CHECKLIST

### **Frontend Deployment (Firebase)**

- [ ] Build production bundle: `npm run build`
- [ ] Test build locally: Preview `dist/index.html`
- [ ] Verify environment variables in Firebase Console
- [ ] Check Firestore rules: `firestore.rules`
- [ ] Check Storage rules: `storage.rules`
- [ ] Deploy: `firebase deploy --only hosting`
- [ ] Verify: Visit production URL
- [ ] Check console for errors

### **DMM Backend Deployment**

- [ ] Create production `.env` on server
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run database migrations (if any)
- [ ] Start service: `uvicorn main:app --host 0.0.0.0 --port 8000`
- [ ] Test health endpoint: `curl http://server:8000/health`
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up SSL certificate
- [ ] Configure firewall rules
- [ ] Set up monitoring/logging

### **Jitta Assistant Deployment**

- [ ] Verify GPU server has CUDA 12.8
- [ ] Install PyTorch with CUDA support
- [ ] Create production `.env` on server
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run data ingestion: via `/ingest` endpoint
- [ ] Start service: `uvicorn server:app --host 0.0.0.0 --port 8003`
- [ ] Test GPU: Check `/status/runtime` shows CUDA device
- [ ] Verify ChromaDB initialized
- [ ] Test query endpoint: `/chat`
- [ ] Monitor GPU usage: `nvidia-smi`

---

## 🎯 SUMMARY

### **Files Organized:**
- ✅ **30+ files** reorganized into proper structure
- ✅ **3 new documentation** files created
- ✅ **10 obsolete scripts** archived
- ✅ **Clear separation** between root repo and app repo

### **Ready to Commit:**
- ✅ Root repo: System docs + backend services
- ✅ Main app repo: Documentation + source code + configs

### **Ready to Deploy:**
- ✅ Frontend: Build and Firebase deploy
- ✅ DMM Backend: Python service deployment
- ✅ Jitta Assistant: GPU server deployment

### **Security:**
- ✅ .gitignore updated to exclude secrets
- ✅ Sensitive files not staged
- ✅ Security documentation in place

---

## 📞 Next Steps

1. **Review this checklist** thoroughly
2. **Update .gitignore** with backup file rules
3. **Commit changes** using recommended structure
4. **Push to remote:** `git push origin main`
5. **Deploy to production** following deployment checklist
6. **Monitor services** after deployment
7. **Update team** about new documentation structure

---

**Checklist Status:** ✅ **READY FOR COMMIT & DEPLOY**  
**Last Verified:** March 3, 2026

**For questions, see:**
- [README_SYSTEM.md](../README_SYSTEM.md) - System overview
- [docs/INDEX.md](peace-script-basic-v1/docs/INDEX.md) - Documentation hub
- [docs/deployment/DEPLOYMENT_STATUS.md](peace-script-basic-v1/docs/deployment/DEPLOYMENT_STATUS.md) - Deployment procedures
