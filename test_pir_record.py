#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from core.sighting_service import sighting_service
from datetime import datetime

# Manually trigger a PIR motion event
timestamp = datetime.now().isoformat()
motion_data = {
    'camera': 'NestCam',
    'type': 'gpio', 
    'confidence': 0.9,
    'duration': 2.0
}

print('📡 Recording test PIR motion event...')
sighting_service._record_motion_event(timestamp, motion_data)
print('✅ PIR motion event recorded to database')
print('🔍 Check dashboard for new motion event')
