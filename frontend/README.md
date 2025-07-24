# Nutflix Frontend

This is the React-based frontend for the Nutflix Platform.

## Setup

```bash
cd frontend
npm install
npm start
```

## Integration with Backend

The frontend communicates with the Flask backend via API endpoints:

- Backend runs on: `http://localhost:8000`
- Frontend runs on: `http://localhost:3000`
- API endpoints: `/api/*`

## Environment Configuration

Create a `.env` file in this directory:

```
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=5000
```

## Build for Production

```bash
npm run build
```

This creates optimized static files in the `build/` directory that can be served by the Flask backend.
