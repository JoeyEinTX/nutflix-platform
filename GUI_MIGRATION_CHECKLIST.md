# GUI Repository Migration Checklist

## 🎯 Primary Goal
Copy working GUI components from your separate repository to the main NutFlix repository to fix missing UI details, emojis, dropdown backgrounds, and camera feeds.

## ✅ Current Status (Main Repo)
- ✅ Flask backend working perfectly
- ✅ CritterCam and NestCam producing 640x480 RGB888 frames  
- ✅ API endpoints responding (GET /api/stream/{camera}/thumbnail)
- ✅ Vite proxy configuration correct (127.0.0.1:8000)
- ✅ CORS headers working
- ❌ Frontend UI components missing proper styling/functionality

## 📁 Files to Copy from GUI Repository

### Core Application Files
- [ ] `frontend/src/App.js` or `App.jsx` (the working version)
- [ ] `frontend/src/App.css` (complete styling)
- [ ] `frontend/src/flask-styles.css` (camera cards, dropdown backgrounds)
- [ ] `frontend/src/index.css` (if different)

### Component Files
- [ ] `frontend/src/components/CameraThumbnail.jsx`
- [ ] `frontend/src/components/Modal.jsx`
- [ ] `frontend/src/components/FullCameraView.jsx`
- [ ] `frontend/src/components/FigmaStyleDashboard_3cards.jsx`
- [ ] Any other working dashboard components

### Service Files
- [ ] `frontend/src/services/api.js` (API integration)

### Configuration Files
- [ ] `frontend/vite.config.js` (check proxy settings)
- [ ] `frontend/package.json` (compare dependencies)

## 🔍 What to Check After Copying

### Dependencies in package.json
- [ ] React versions match (`^18.2.0`)
- [ ] axios for API calls (`^1.4.0`)
- [ ] framer-motion (if used for animations)
- [ ] Any GUI-specific packages

### Import Paths
- [ ] All component imports use correct paths
- [ ] CSS imports point to existing files
- [ ] Service imports work correctly

### API Integration
- [ ] Camera feeds display live thumbnails
- [ ] API calls to `/api/stream/CritterCam/thumbnail` work
- [ ] API calls to `/api/stream/NestCam/thumbnail` work
- [ ] Error handling for missing cameras (OuterCam)

### UI Elements
- [ ] Dropdown backgrounds render properly
- [ ] All emojis display correctly (📊 🔬 🎬 ⚙️ 🐿️)
- [ ] Camera status indicators work
- [ ] Live feed indicators display
- [ ] Motion badges appear when needed

## 🚀 After Migration Steps

1. **Copy files** from GUI repository to main repository
2. **Install dependencies**: `npm install`
3. **Restart frontend**: `./start_frontend.sh`
4. **Test in browser**: http://localhost:3000/
5. **Verify camera feeds** are displaying
6. **Check dropdown styling** works properly
7. **Confirm all UI details** are present

## 🛠️ Troubleshooting

If issues persist after copying:
- Check browser console for JavaScript errors
- Verify all file paths are correct
- Ensure Flask backend is still running on port 8000
- Test API endpoints directly with curl
- Compare working GUI repo file structure to main repo

## 📞 Next Steps

Once you've copied the files from your GUI repository, restart the frontend and test. The backend infrastructure is already working perfectly - we just need the correct frontend components to display the data properly.
