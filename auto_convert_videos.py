#!/usr/bin/env python3
"""
Auto Video Conversion Service for Nutflix Platform

Watches /recordings/ directory for new .mp4 files and automatically converts 
non-H.264 videos to H.264 + AAC format for optimal web playback.

Output files are saved as <original_name>_h264.mp4

Features:
- Continuous monitoring using watchdog
- Codec detection with ffprobe 
- Skip conversion if already H.264
- Web-optimized encoding with faststart and GOP=30
- Comprehensive logging
- Error handling and retry logic

Usage:
    python3 auto_convert_videos.py
"""

import os
import sys
import time
import json
import logging
import subprocess
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
CLIPS_DIR = Path(__file__).parent / "clips"
LOG_FILE = Path(__file__).parent / "auto_convert.log"
FFMPEG_TIMEOUT = 300  # 5 minutes timeout for conversion
RETRY_DELAY = 30  # Wait 30 seconds before retry

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class VideoConverter:
    """Handles video conversion operations"""
    
    def __init__(self):
        self.conversion_queue = []
        self.processing = False
        
    def get_video_codec(self, video_path):
        """
        Use ffprobe to detect video codec
        Returns codec name or None if detection fails
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_streams', '-select_streams', 'v:0', str(video_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if 'streams' in data and len(data['streams']) > 0:
                    codec = data['streams'][0].get('codec_name', 'unknown')
                    logger.info(f"Detected codec for {video_path.name}: {codec}")
                    return codec
            else:
                logger.error(f"ffprobe failed for {video_path}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error(f"ffprobe timeout for {video_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ffprobe output for {video_path}: {e}")
        except Exception as e:
            logger.error(f"Error detecting codec for {video_path}: {e}")
            
        return None
    
    def is_h264(self, video_path):
        """Check if video is already H.264 encoded"""
        codec = self.get_video_codec(video_path)
        return codec == 'h264'
    
    def convert_to_h264(self, input_path):
        """
        Convert video to H.264 + AAC with web optimization
        
        FFmpeg settings:
        - H.264 video codec with medium preset
        - AAC audio codec  
        - GOP size 30 for web streaming
        - faststart for web playback
        - Maintain original resolution
        """
        output_path = input_path.with_name(f"{input_path.stem}_h264.mp4")
        
        # Skip if output already exists
        if output_path.exists():
            logger.info(f"H.264 version already exists: {output_path.name}")
            return True
            
        logger.info(f"Starting conversion: {input_path.name} -> {output_path.name}")
        
        # FFmpeg command optimized for web playback
        cmd = [
            'ffmpeg', '-y',  # Overwrite output file
            '-i', str(input_path),
            '-c:v', 'libx264',          # H.264 video codec
            '-preset', 'medium',         # Balanced speed/quality
            '-crf', '23',               # Good quality setting
            '-g', '30',                 # GOP size 30 frames
            '-keyint_min', '30',        # Minimum keyframe interval
            '-c:a', 'aac',              # AAC audio codec
            '-b:a', '128k',             # Audio bitrate
            '-movflags', '+faststart',   # Enable fast start for web
            '-pix_fmt', 'yuv420p',      # Ensure compatibility
            str(output_path)
        ]
        
        try:
            # Run conversion with timeout
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=FFMPEG_TIMEOUT
            )
            
            if result.returncode == 0:
                # Verify output file was created and has reasonable size
                if output_path.exists() and output_path.stat().st_size > 1024:
                    logger.info(f"✅ Conversion successful: {output_path.name}")
                    logger.info(f"   Original: {input_path.stat().st_size / (1024*1024):.1f}MB")
                    logger.info(f"   Converted: {output_path.stat().st_size / (1024*1024):.1f}MB")
                    return True
                else:
                    logger.error(f"❌ Output file invalid: {output_path}")
                    if output_path.exists():
                        output_path.unlink()  # Remove invalid file
                    return False
            else:
                logger.error(f"❌ FFmpeg conversion failed for {input_path.name}")
                logger.error(f"   Command: {' '.join(cmd)}")
                logger.error(f"   Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Conversion timeout for {input_path.name}")
            if output_path.exists():
                output_path.unlink()  # Remove partial file
            return False
        except Exception as e:
            logger.error(f"❌ Conversion error for {input_path.name}: {e}")
            if output_path.exists():
                output_path.unlink()  # Remove partial file
            return False
    
    def process_video(self, video_path):
        """Process a single video file"""
        try:
            video_path = Path(video_path)
            
            # Validate input file
            if not video_path.exists():
                logger.warning(f"Video file not found: {video_path}")
                return
                
            if not video_path.suffix.lower() == '.mp4':
                logger.info(f"Skipping non-MP4 file: {video_path.name}")
                return
                
            # Skip if filename already contains _h264
            if '_h264' in video_path.stem:
                logger.info(f"Skipping already converted file: {video_path.name}")
                return
                
            # Check if already H.264
            if self.is_h264(video_path):
                logger.info(f"Already H.264, skipping: {video_path.name}")
                return
                
            # Convert to H.264
            success = self.convert_to_h264(video_path)
            
            if not success:
                logger.warning(f"Conversion failed for {video_path.name}, will retry later")
                # Add to retry queue after delay
                threading.Timer(RETRY_DELAY, lambda: self.process_video(video_path)).start()
                
        except Exception as e:
            logger.error(f"Error processing {video_path}: {e}")

class VideoWatchHandler(FileSystemEventHandler):
    """Handles file system events for video files"""
    
    def __init__(self, converter):
        self.converter = converter
        
    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Only process .mp4 files
        if file_path.suffix.lower() == '.mp4':
            logger.info(f"📁 New video detected: {file_path.name}")
            
            # Wait a moment for file to be fully written
            time.sleep(2)
            
            # Process in separate thread to avoid blocking watcher
            threading.Thread(
                target=self.converter.process_video, 
                args=(file_path,),
                daemon=True
            ).start()
    
    def on_moved(self, event):
        """Handle file moves (sometimes used instead of creation)"""
        if event.is_directory:
            return
            
        file_path = Path(event.dest_path)
        
        if file_path.suffix.lower() == '.mp4':
            logger.info(f"📁 Video moved to recordings: {file_path.name}")
            
            # Wait a moment for file to be fully written
            time.sleep(2)
            
            # Process in separate thread
            threading.Thread(
                target=self.converter.process_video, 
                args=(file_path,),
                daemon=True
            ).start()

def scan_existing_videos(converter):
    """Scan existing videos in clips directory"""
    logger.info("🔍 Scanning existing videos for conversion...")
    
    if not CLIPS_DIR.exists():
        logger.warning(f"Clips directory not found: {CLIPS_DIR}")
        return
    
    # Find all MP4 files recursively in clips directory
    mp4_files = list(CLIPS_DIR.rglob("*.mp4"))
    non_h264_files = []
    
    for video_file in mp4_files:
        # Skip _h264 files
        if '_h264' not in video_file.stem:
            non_h264_files.append(video_file)
    
    logger.info(f"Found {len(non_h264_files)} videos to check for conversion")
    
    # Process existing files
    for video_file in non_h264_files:
        threading.Thread(
            target=converter.process_video,
            args=(video_file,),
            daemon=True
        ).start()
        time.sleep(1)  # Stagger processing to avoid overwhelming system

def main():
    """Main function - start the video conversion service"""
    logger.info("🎬 Starting Auto Video Conversion Service")
    logger.info(f"📂 Monitoring directory: {CLIPS_DIR}")
    logger.info(f"📝 Log file: {LOG_FILE}")
    
    # Create clips directory if it doesn't exist
    CLIPS_DIR.mkdir(exist_ok=True)
    
    # Initialize converter
    converter = VideoConverter()
    
    # Scan existing videos
    scan_existing_videos(converter)
    
    # Setup file watcher (recursive to monitor subdirectories)
    event_handler = VideoWatchHandler(converter)
    observer = Observer()
    observer.schedule(event_handler, str(CLIPS_DIR), recursive=True)
    
    # Start watching
    observer.start()
    logger.info("✅ Video conversion service started successfully")
    logger.info("   - Watching for new .mp4 files recursively")
    logger.info("   - Converting non-H.264 videos automatically")
    logger.info("   - Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Stopping video conversion service...")
        observer.stop()
    
    observer.join()
    logger.info("✅ Video conversion service stopped")

if __name__ == "__main__":
    main()
