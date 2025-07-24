# Nutflix Platform - Pi GUI Submodule Setup Guide

**⚠️ IMPORTANT: This guide is for execution on your Raspberry Pi where the main nutflix-platform repository lives.**

## Pre-Setup Safety Check

### 1. Backup Your Current Work
```bash
# Navigate to your nutflix-platform directory on Pi
cd /path/to/nutflix-platform

# Create a backup of current state
git status                           # Check current status
git add . && git commit -m "Backup before GUI submodule setup"

# Create a branch backup (extra safety)
git branch backup-before-gui-submodule

# Backup the frontend directory specifically
cp -r frontend frontend_backup_$(date +%Y%m%d_%H%M%S)
```

### 2. Verify Repository State
```bash
# Ensure you're on main branch
git branch                          # Should show * main

# Ensure working tree is clean
git status                          # Should show "nothing to commit, working tree clean"

# If you have uncommitted changes, commit them first:
# git add .
# git commit -m "Save current work before submodule setup"
```

## Phase 1: Set Up Authentication (if needed)

### Option A: GitHub Personal Access Token (Recommended)
```bash
# If the codespaces-react repo is private, you'll need authentication
# Generate a PAT at: https://github.com/settings/tokens
# Then configure git:
git config --global credential.helper store

# The first git operation will prompt for username/token
```

### Option B: SSH Key (Alternative)
```bash
# If you prefer SSH and have keys set up:
# The submodule command would use: git@github.com:JoeyEinTX/codespaces-react.git
```

## Phase 2: Add GUI as Submodule

### Step 1: Add the Submodule
```bash
# Navigate to your main repo root
cd /path/to/nutflix-platform

# Add GUI repo as submodule named 'gui'
git submodule add https://github.com/JoeyEinTX/codespaces-react.git gui

# If that fails with 403 error, try SSH:
# git submodule add git@github.com:JoeyEinTX/codespaces-react.git gui
```

### Step 2: Verify Submodule Setup
```bash
# Check .gitmodules file was created
cat .gitmodules

# Should show:
# [submodule "gui"]
#     path = gui
#     url = https://github.com/JoeyEinTX/codespaces-react.git

# Verify gui directory exists
ls -la gui/

# Check submodule status
git submodule status
```

### Step 3: Commit the Submodule
```bash
# Add and commit the submodule configuration
git add .gitmodules gui
git commit -m "Added GUI as submodule"

# Push to remote
git push origin main
```

## Phase 3: Update Deployment Scripts

### Step 1: Copy the Management Script
Create the file `manage_gui.sh` with the content from the previous response, or:

```bash
# Download the management script (if you have it in another location)
# wget https://raw.githubusercontent.com/your-repo/manage_gui.sh
# chmod +x manage_gui.sh

# Or create it manually with the content provided earlier
```

### Step 2: Update Frontend Start Script
```bash
# Backup current start script
cp start_frontend.sh start_frontend_backup.sh

# Edit start_frontend.sh to support both gui and frontend
```

Create new `start_frontend.sh`:
```bash
#!/bin/bash
echo "🚀 Starting Nutflix Frontend..."

# Check if GUI submodule exists and is preferred
if [ -d "gui" ] && [ -f "gui/package.json" ]; then
    echo "Using GUI submodule (React)"
    echo "Frontend will run on: http://localhost:3000"
    echo "Press Ctrl+C to stop"
    cd gui
    npm install
    npm start
else
    echo "Using local frontend (React)"
    echo "Frontend will run on: http://localhost:3000"
    echo "Press Ctrl+C to stop"
    cd frontend
    npm install
    npm start
fi
```

## Phase 4: Test the Integration

### Step 1: Test GUI Submodule
```bash
# Navigate to gui directory
cd gui

# Install dependencies
npm install

# Test build
npm run build

# Test development server (Ctrl+C to stop)
npm start
```

### Step 2: Test Backend Integration
```bash
# In another terminal, start backend
cd /path/to/nutflix-platform
./start_backend.sh

# Verify API is accessible from frontend
# Frontend should proxy to http://localhost:8000
```

### Step 3: Full System Test
```bash
# Terminal 1: Start backend
./start_backend.sh

# Terminal 2: Start frontend (now using GUI submodule)
./start_frontend.sh

# Test in browser:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## Phase 5: Future Workflow

### Updating GUI from Codespaces
When you make changes in your codespaces-react repository:

```bash
# On Pi, pull latest GUI changes
cd /path/to/nutflix-platform
git submodule update --remote gui

# Commit the submodule update
git add gui
git commit -m "Updated GUI submodule to latest version"
git push origin main
```

### Working with Both Repositories
```bash
# To work on GUI locally on Pi:
cd gui
# Make changes, commit, push as normal git repo

# To update main platform with GUI changes:
cd ..  # Back to main repo
git add gui
git commit -m "Updated GUI submodule"
git push origin main
```

## Troubleshooting

### If Submodule Add Fails
```bash
# Remove any partial submodule setup
git submodule deinit gui
rm -rf .git/modules/gui
git rm --cached gui
rm -rf gui

# Try again with different URL format or authentication
```

### If GUI Won't Start
```bash
# Check Node.js version
node --version
npm --version

# Clear npm cache
cd gui
rm -rf node_modules package-lock.json
npm install
```

### Rollback Plan (if something goes wrong)
```bash
# Switch back to backup branch
git checkout backup-before-gui-submodule

# Or remove submodule and restore frontend
git submodule deinit gui
git rm gui
rm -rf .git/modules/gui
git commit -m "Removed GUI submodule"

# Restore original frontend if needed
# cp -r frontend_backup_* frontend
```

## Success Indicators

✅ `.gitmodules` file exists and contains GUI submodule configuration  
✅ `gui/` directory exists with React app files  
✅ `git submodule status` shows GUI submodule  
✅ `npm start` works in `gui/` directory  
✅ Frontend loads at http://localhost:3000  
✅ Backend API accessible at http://localhost:8000  
✅ GUI can communicate with backend API  

## Next Steps After Success

1. Test all existing functionality still works
2. Update documentation references from `frontend/` to `gui/`
3. Consider removing old `frontend/` directory after thorough testing
4. Update any CI/CD scripts to handle submodules
5. Document the new workflow for other team members

---

**Remember**: Take your time, test each step, and don't hesitate to create additional backups at any point. Your progress is valuable and we want to preserve it!
