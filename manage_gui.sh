#!/bin/bash

# Nutflix Platform GUI Management Script
echo "🎬 Nutflix Platform GUI Manager"
echo "=================================="

# Function to setup GUI submodule
setup_gui_submodule() {
    echo "Setting up GUI as submodule..."
    
    # Check if GUI submodule already exists
    if [ -d "gui" ]; then
        echo "GUI submodule already exists. Updating..."
        git submodule update --remote gui
    else
        echo "Adding GUI as submodule..."
        # Try HTTPS first, fall back to SSH if needed
        git submodule add https://github.com/JoeyEinTX/codespaces-react.git gui || \
        git submodule add git@github.com:JoeyEinTX/codespaces-react.git gui
    fi
}

# Function to sync changes between frontend and gui
sync_frontend_to_gui() {
    echo "Syncing current frontend to GUI repo..."
    if [ -d "gui" ]; then
        echo "Copying frontend changes to GUI submodule..."
        rsync -av --exclude=node_modules frontend/ gui/
        cd gui
        git add .
        git commit -m "Sync from main platform frontend"
        git push
        cd ..
        git add gui
        git commit -m "Updated GUI submodule"
    else
        echo "GUI submodule not found. Run setup first."
    fi
}

# Function to update GUI submodule
update_gui() {
    echo "Updating GUI submodule..."
    git submodule update --remote gui
    git add gui
    git commit -m "Updated GUI submodule to latest version"
}

# Function to start GUI development
start_gui_dev() {
    echo "Starting GUI development server..."
    if [ -d "gui" ]; then
        cd gui
        npm install
        npm start
    else
        echo "GUI submodule not found. Using local frontend..."
        cd frontend
        npm install
        npm start
    fi
}

# Main menu
case "$1" in
    setup)
        setup_gui_submodule
        ;;
    sync)
        sync_frontend_to_gui
        ;;
    update)
        update_gui
        ;;
    dev)
        start_gui_dev
        ;;
    *)
        echo "Usage: $0 {setup|sync|update|dev}"
        echo ""
        echo "Commands:"
        echo "  setup  - Set up GUI as git submodule"
        echo "  sync   - Sync current frontend to GUI repo"
        echo "  update - Update GUI submodule to latest"
        echo "  dev    - Start GUI development server"
        echo ""
        echo "Examples:"
        echo "  ./manage_gui.sh setup   # First time setup"
        echo "  ./manage_gui.sh sync    # Copy local changes to GUI repo"
        echo "  ./manage_gui.sh update  # Pull latest GUI changes"
        echo "  ./manage_gui.sh dev     # Start development server"
        ;;
esac
