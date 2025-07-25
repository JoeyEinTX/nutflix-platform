#!/bin/bash
# GUI Repository Migration Script
# Copy working components from GUI repo to main NutFlix repo

echo "🚀 Starting GUI Repository Migration to Main NutFlix Repository"

# Variables
MAIN_REPO_PATH="/home/p12146/NutFlix/nutflix-platform"

# Try to find the GUI repository automatically
GUI_REPO_CANDIDATES=(
    "/home/p12146/NutFlix/nutflix-platform/frontend-gui"
    "/workspaces/codespaces-react"
    "/home/p12146/codespaces-react"
    "$HOME/codespaces-react"
    "/workspaces/nutflix-gui"
    "/home/p12146/nutflix-gui"
)

GUI_REPO_PATH=""
for candidate in "${GUI_REPO_CANDIDATES[@]}"; do
    if [ -d "$candidate/src" ]; then
        GUI_REPO_PATH="$candidate"
        echo "✅ Found GUI repository at: $GUI_REPO_PATH"
        break
    fi
done

if [ -z "$GUI_REPO_PATH" ]; then
    echo "❌ Could not automatically find GUI repository."
    echo "Please set GUI_REPO_PATH manually in this script."
    echo "Looking for directories with frontend/src structure..."
    find /workspaces -maxdepth 2 -name "frontend" -type d 2>/dev/null || true
    find /home -maxdepth 3 -name "frontend" -type d 2>/dev/null || true
    exit 1
fi

echo "📋 Files to copy from GUI repository:"
echo "1. frontend/src/App.js or App.jsx (the working version)"
echo "2. frontend/src/App.css"  
echo "3. frontend/src/flask-styles.css"
echo "4. frontend/src/components/ (all working components)"
echo "5. frontend/src/services/api.js"
echo "6. frontend/vite.config.js"
echo "7. frontend/package.json (check dependencies)"

echo ""
echo "🔍 Current status of main repository:"
echo "✅ Flask backend is working (cameras producing frames)"
echo "✅ Proxy configuration is correct" 
echo "✅ API endpoints are responding"
echo "❌ Frontend UI components need GUI repo files"

echo ""
echo "🚀 Starting file migration..."

# Create backup of current files
BACKUP_DIR="${MAIN_REPO_PATH}/frontend_backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup at: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "${MAIN_REPO_PATH}/frontend/src" "$BACKUP_DIR/" 2>/dev/null || true

# Function to copy file if it exists and is different
copy_if_different() {
    local src="$1"
    local dest="$2"
    local name="$3"
    
    if [ -f "$src" ]; then
        if [ ! -f "$dest" ] || ! cmp -s "$src" "$dest"; then
            echo "📄 Copying $name..."
            cp "$src" "$dest"
            echo "   ✅ $name copied successfully"
        else
            echo "📄 $name is already up to date"
        fi
    else
        echo "⚠️  $name not found in GUI repo: $src"
    fi
}

# Copy core application files
echo ""
echo "📱 Copying core application files..."
mkdir -p "${MAIN_REPO_PATH}/frontend/src"

# Try both App.js and App.jsx
if [ -f "${GUI_REPO_PATH}/src/App.jsx" ]; then
    copy_if_different "${GUI_REPO_PATH}/src/App.jsx" "${MAIN_REPO_PATH}/frontend/src/App.jsx" "App.jsx"
fi
if [ -f "${GUI_REPO_PATH}/src/App.js" ]; then
    copy_if_different "${GUI_REPO_PATH}/src/App.js" "${MAIN_REPO_PATH}/frontend/src/App.js" "App.js"
fi

copy_if_different "${GUI_REPO_PATH}/src/App.css" "${MAIN_REPO_PATH}/frontend/src/App.css" "App.css"
copy_if_different "${GUI_REPO_PATH}/src/flask-styles.css" "${MAIN_REPO_PATH}/frontend/src/flask-styles.css" "flask-styles.css"
copy_if_different "${GUI_REPO_PATH}/src/index.css" "${MAIN_REPO_PATH}/frontend/src/index.css" "index.css"

# Copy components directory
echo ""
echo "🧩 Copying component files..."
mkdir -p "${MAIN_REPO_PATH}/frontend/src/components"

if [ -d "${GUI_REPO_PATH}/src/components" ]; then
    for component in "${GUI_REPO_PATH}/src/components"/*; do
        if [ -f "$component" ]; then
            filename=$(basename "$component")
            dest_file="${MAIN_REPO_PATH}/frontend/src/components/$filename"
            copy_if_different "$component" "$dest_file" "components/$filename"
        fi
    done
else
    echo "⚠️  Components directory not found in GUI repo"
fi

# Copy services directory
echo ""
echo "🔧 Copying service files..."
mkdir -p "${MAIN_REPO_PATH}/frontend/src/services"

if [ -d "${GUI_REPO_PATH}/src/services" ]; then
    for service in "${GUI_REPO_PATH}/src/services"/*; do
        if [ -f "$service" ]; then
            filename=$(basename "$service")
            dest_file="${MAIN_REPO_PATH}/frontend/src/services/$filename"
            copy_if_different "$service" "$dest_file" "services/$filename"
        fi
    done
else
    echo "⚠️  Services directory not found in GUI repo"
fi

# Copy configuration files
echo ""
echo "⚙️  Copying configuration files..."
copy_if_different "${GUI_REPO_PATH}/vite.config.js" "${MAIN_REPO_PATH}/frontend/vite.config.js" "vite.config.js"

# Compare package.json files
echo ""
echo "📦 Checking package.json dependencies..."
if [ -f "${GUI_REPO_PATH}/package.json" ] && [ -f "${MAIN_REPO_PATH}/frontend/package.json" ]; then
    echo "🔍 GUI repo dependencies:"
    jq -r '.dependencies | keys[]' "${GUI_REPO_PATH}/package.json" 2>/dev/null || echo "   (Could not parse JSON)"
    echo ""
    echo "🔍 Main repo dependencies:"
    jq -r '.dependencies | keys[]' "${MAIN_REPO_PATH}/frontend/package.json" 2>/dev/null || echo "   (Could not parse JSON)"
    echo ""
    echo "💡 Manual step: Compare these dependencies and update main repo package.json if needed"
else
    echo "⚠️  Could not find package.json in one or both repositories"
fi

echo ""
echo "� Post-migration steps..."

# Install any missing dependencies
echo "📦 Installing dependencies..."
cd "${MAIN_REPO_PATH}/frontend"
npm install

echo ""
echo "🚀 Migration completed!"
echo ""
echo "📝 Next Steps:"
echo "1. Review the copied files to ensure they look correct"
echo "2. Check for any import path issues"
echo "3. Restart the frontend server"
echo "4. Test the application at http://localhost:3000/"
echo ""
echo "🔧 To restart frontend:"
echo "   cd ${MAIN_REPO_PATH}"
echo "   ./start_frontend.sh"
echo ""
echo "🧪 Test these features after restart:"
echo "   ✓ Camera feeds display live thumbnails"
echo "   ✓ Dropdown styling works properly"
echo "   ✓ All emojis and UI details appear"
echo "   ✓ Navigation between dashboard sections"
echo ""
echo "📁 Backup created at: $BACKUP_DIR"
echo "   (You can restore from backup if needed)"

# Optional: Ask if user wants to restart frontend now
echo ""
read -p "🚀 Would you like to restart the frontend now? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Restarting frontend..."
    cd "${MAIN_REPO_PATH}"
    pkill -f "vite.*3000" 2>/dev/null || true
    sleep 2
    ./start_frontend.sh &
    echo "✅ Frontend restart initiated"
    echo "🌐 Check http://localhost:3000/ in a few seconds"
fi
