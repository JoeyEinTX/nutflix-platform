# Static Image Assets for Nutflix UI

This directory contains static image assets that are part of the UI design and should be committed to the repository.

## Seasonal Modal Backgrounds

The following bark texture images are required for the Modal component's seasonal theming:

- `bark-spring.jpg` - Light brown bark with green tints
- `bark-summer.jpg` - Rich brown bark texture  
- `bark-fall.jpg` - Orange-brown bark with autumn colors
- `bark-winter.jpg` - Dark bark with cooler tones

## Adding Your Images

1. Copy your bark texture images to this directory
2. Use these exact filenames for the seasonal modal backgrounds to work
3. Run `git add frontend/public/images/bark-*.jpg` to track them
4. Commit them: `git commit -m "Add seasonal bark texture backgrounds"`

## Professional Repository Management

The .gitignore has been updated to:
- ✅ **INCLUDE** static UI assets in `frontend/public/images/`
- ❌ **EXCLUDE** generated camera recordings, clips, and thumbnails

This ensures your UI assets are always available when deploying to new devices.
