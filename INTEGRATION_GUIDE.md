# Nutflix Platform Integration Guide

## 🚀 Professional React Integration

This guide shows how to integrate your React GUI with the Nutflix Platform backend.

## Architecture Overview

```
nutflix-platform/
├── frontend/          # React application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── .env
├── dashboard/         # Flask backend (API)
│   ├── app_with_react.py
│   └── routes/
└── core/             # Shared platform code
```

## Setup Instructions

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Start the Backend (Flask API)

In one terminal:
```bash
cd /workspaces/nutflix-platform
python dashboard/app_with_react.py
```

Backend will run on: `http://localhost:8000`

### 3. Start the Frontend (React)

In another terminal:
```bash
cd frontend
npm start
```

Frontend will run on: `http://localhost:3000`

## Development Workflow

### Option 1: Development Mode (Recommended)
- Run Flask backend on port 8000
- Run React frontend on port 3000
- React proxy sends API calls to Flask
- Hot reloading for both frontend and backend

### Option 2: Production Mode
```bash
# Build React app
cd frontend
npm run build

# Start Flask with built React files
cd ..
python dashboard/app_with_react.py
```

Access the app at: `http://localhost:8000/app`

## API Integration

The React app communicates with Flask via these endpoints:

### System API
- `GET /api/status` - System status and module availability
- `GET /health` - Health check

### Clips API
- `GET /api/clips` - List video clips
- `GET /api/clips/:id` - Get specific clip
- `DELETE /api/clips/:id` - Delete clip

### Research API
- `GET /api/research/sightings` - Wildlife sightings data
- `GET /api/research/trends` - Activity trends

### Settings API
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings

### Stream API
- `GET /api/stream/status` - Stream status
- `POST /api/stream/start` - Start stream
- `POST /api/stream/stop` - Stop stream

## Environment Configuration

### Frontend (.env)
```
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=5000
REACT_APP_PLATFORM_NAME=Nutflix
REACT_APP_VERSION=1.0.0
```

### Backend CORS Configuration
The Flask app is configured to accept requests from:
- `http://localhost:3000` (React dev server)
- GitHub Codespaces preview URLs
- Custom domains (configurable)

## Migrating Your Existing React Code

To integrate your existing React GUI:

1. **Copy your components** to `frontend/src/components/`
2. **Update imports** to use the `apiService` from `services/api.js`
3. **Replace API calls** with the standardized API service methods
4. **Update styling** to work with the base CSS structure
5. **Test integration** with the Flask backend

## Example Component Integration

```javascript
### Step 2: Update API Calls
Replace direct fetch calls with the standardized API service:

```javascript
// Before (direct fetch)
const data = await fetch('/api/clips').then(r => r.json());

// After (using apiService)
import { apiService } from '../services/api';
const data = await apiService.getClips();
```

## Deployment Options

### Local Deployment
- Single machine running both Flask (with full camera/AI features) and React
- Use production build served by Flask

### Containerized Deployment
```

## Deployment Options

### Local Deployment
- Single machine running both Flask and React
- Use production build served by Flask

### Containerized Deployment
```dockerfile
# Frontend build
FROM node:18 AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Backend with frontend
FROM python:3.9
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
COPY --from=frontend-build /app/frontend/build ./frontend/build
EXPOSE 8000
CMD ["python", "dashboard/app_with_react.py"]
```

### Separate Services Deployment
- Frontend: Deploy React build to CDN/static hosting
- Backend: Deploy Flask API to server
- Configure CORS for cross-origin requests

## Troubleshooting

### CORS Issues
If you get CORS errors, check:
1. Flask-CORS is installed: `pip install flask-cors`
2. Frontend URL is in CORS origins list
3. API calls use correct base URL

### API Connection Issues
1. Verify backend is running on port 8000
2. Check firewall/network settings
3. Ensure API endpoints are registered correctly

### Build Issues
1. Run `npm install` in frontend directory
2. Check Node.js version compatibility
3. Clear npm cache: `npm cache clean --force`

## Next Steps

1. **Copy your React code** into the `frontend/` directory
2. **Test API integration** with existing backend
3. **Enhance components** using the apiService
4. **Add error handling** and loading states
5. **Implement authentication** if needed
6. **Set up production deployment**

This structure provides a professional, scalable foundation for your Nutflix Platform GUI! 🐿️
