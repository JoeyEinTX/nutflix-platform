# Nutflix Platform - GUI Integration Strategy

## Current Setup
- **Main Repo**: nutflix-platform (backend + current frontend)
- **GUI Repo**: codespaces-react (dedicated GUI development)
- **Integration**: Git submodules

## Directory Structure After Integration
```
nutflix-platform/
├── gui/                    # Git submodule → codespaces-react
├── frontend/              # Current React app (backup/transition)
├── dashboard/             # Flask backend
├── core/                  # Core services
└── manage_gui.sh          # GUI management script
```

## Workflow

### 1. Initial Setup
```bash
# Set up GUI submodule
./manage_gui.sh setup

# Or manually:
git submodule add https://github.com/JoeyEinTX/codespaces-react.git gui
git commit -m "Added GUI as submodule"
```

### 2. Development Workflow
```bash
# Work on GUI in separate codespace (codespaces-react repo)
# Then update main platform:
./manage_gui.sh update
```

### 3. Sync Existing Frontend to GUI
```bash
# Copy current frontend to GUI repo
./manage_gui.sh sync
```

### 4. Production Deployment
```bash
# Build GUI
cd gui && npm run build

# Serve static files through Flask or separate CDN
# Backend API: http://your-pi:8000/api
# Frontend: http://your-pi:3000 or CDN
```

## Benefits

✅ **Separate Development**: GUI team works independently
✅ **Version Control**: Pin specific GUI versions in main repo  
✅ **Independent Deployment**: GUI can be deployed to CDN
✅ **Clean Architecture**: Backend and Frontend completely separated
✅ **Team Collaboration**: Different people on GUI vs backend

## Deployment Options

### Option A: Submodule Integration (Recommended)
- Main repo references specific GUI version
- GUI deployed as static files
- Backend serves API only

### Option B: Separate Deployments
- GUI: Deploy to Vercel/Netlify/CDN
- Backend: Deploy to Pi
- Cross-origin configured properly

## Next Steps

1. Choose integration approach
2. Set up submodule with `./manage_gui.sh setup`
3. Configure CORS for API access
4. Update deployment scripts
5. Test full integration
