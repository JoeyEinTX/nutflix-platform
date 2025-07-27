# NutFlix Streaming Service Removal & On-Demand Implementation Plan

## Current Issues
1. **Dual Streaming Services**: Both standalone StreamServer (port 5000) and dashboard stream routes (port 8000)
2. **Resource Conflicts**: Multiple CameraManager instances competing for hardware access
3. **Unnecessary Resource Usage**: Continuous streaming even when no one is watching

## Proposed Solution: On-Demand Live Viewing

### What We've Implemented:
1. **OnDemandCameraView Component**: Full-screen camera viewer with two modes:
   - **Snapshot Mode** (default): Updates every 3 seconds, low bandwidth
   - **Live Mode** (on-demand): Real-time MJPEG stream, higher bandwidth

2. **Enhanced Stream API**: Updated backend to support camera-specific streaming

### Next Steps to Complete the Migration:

1. **Remove Standalone StreamServer from NutPod**:
   - Remove StreamServer initialization from `devices/nutpod/main.py`
   - Keep only the dashboard's integrated streaming

2. **Update Camera Access Pattern**:
   - Ensure only one CameraManager instance is used
   - Share the same instance between motion detection and streaming

3. **Add Bandwidth Optimization**:
   - Implement stream connection counting
   - Auto-stop streams when no viewers

### Benefits:
- **Reduced Resource Usage**: Cameras only stream when actively viewed
- **No Hardware Conflicts**: Single CameraManager instance
- **Better User Experience**: Choice between low-bandwidth snapshots and high-quality live stream
- **Scalable**: Can handle multiple simultaneous viewers efficiently

### Implementation Status:
✅ OnDemandCameraView component created
✅ Dashboard updated to use on-demand viewing
✅ Enhanced stream API endpoints  
🔄 Need to remove redundant StreamServer
🔄 Need to test camera access coordination
