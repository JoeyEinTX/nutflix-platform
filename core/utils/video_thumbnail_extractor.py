"""
Video Thumbnail Extractor for NutFlix

Extracts thumbnails from recorded video clips and manages thumbnail storage.
Used to create thumbnails for Recent Sightings display from motion-triggered video recordings.
"""

import os
import cv2
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)

class VideoThumbnailExtractor:
    """Extracts thumbnails from video clips and manages thumbnail storage"""
    
    def __init__(self, thumbnails_dir: str = "./thumbnails"):
        self.thumbnails_dir = Path(thumbnails_dir)
        self.thumbnails_dir.mkdir(exist_ok=True)
        logger.info(f"📸 VideoThumbnailExtractor initialized with thumbnails_dir: {self.thumbnails_dir}")
    
    def extract_thumbnail_from_video(self, video_path: str, timestamp: str = None, camera_name: str = None) -> Optional[str]:
        """
        Extract a thumbnail from a video file
        
        Args:
            video_path: Path to the video file
            timestamp: Timestamp for filename (optional, will extract from video_path if None)
            camera_name: Camera name for filename (optional, will extract from video_path if None)
            
        Returns:
            str: Path to the created thumbnail file, or None if failed
        """
        try:
            video_path = Path(video_path)
            
            if not video_path.exists():
                logger.error(f"❌ Video file not found: {video_path}")
                return None
            
            # Extract metadata from filename if not provided
            if not timestamp or not camera_name:
                extracted_meta = self._extract_metadata_from_filename(video_path.name)
                if not timestamp:
                    timestamp = extracted_meta.get('timestamp', datetime.now().isoformat())
                if not camera_name:
                    camera_name = extracted_meta.get('camera', 'unknown')
            
            # Generate thumbnail filename
            safe_timestamp = timestamp.replace(':', '-').replace('T', '_').split('.')[0]
            thumbnail_filename = f"{camera_name}_{safe_timestamp}_clip.jpg"
            thumbnail_path = self.thumbnails_dir / thumbnail_filename
            
            # Extract frame using OpenCV
            success = self._extract_frame_opencv(str(video_path), str(thumbnail_path), camera_name, safe_timestamp)
            
            if success:
                logger.info(f"📸 Video thumbnail extracted: {thumbnail_path}")
                return str(thumbnail_path)
            else:
                # Fallback to ffmpeg
                logger.info(f"🔄 OpenCV extraction failed, trying ffmpeg...")
                success = self._extract_frame_ffmpeg(str(video_path), str(thumbnail_path))
                
                if success:
                    # Add overlay to ffmpeg-extracted frame
                    self._add_overlay_to_thumbnail(str(thumbnail_path), camera_name, safe_timestamp)
                    logger.info(f"📸 Video thumbnail extracted with ffmpeg: {thumbnail_path}")
                    return str(thumbnail_path)
                else:
                    logger.error(f"❌ Failed to extract thumbnail from {video_path}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error extracting thumbnail from {video_path}: {e}")
            return None
    
    def _extract_frame_opencv(self, video_path: str, thumbnail_path: str, camera_name: str, timestamp: str) -> bool:
        """Extract a frame using OpenCV"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.warning(f"⚠️ Could not open video with OpenCV: {video_path}")
                return False
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            if total_frames == 0:
                logger.warning(f"⚠️ Video has no frames: {video_path}")
                cap.release()
                return False
            
            # Extract frame from middle of video (better chance of activity)
            middle_frame = total_frames // 2
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            
            ret, frame = cap.read()
            cap.release()
            
            if not ret or frame is None:
                logger.warning(f"⚠️ Could not read frame from video: {video_path}")
                return False
            
            # Resize to thumbnail size (320x240 for consistency with motion thumbnails)
            height, width = frame.shape[:2]
            thumb_width = 320
            thumb_height = int(height * (thumb_width / width))
            thumbnail = cv2.resize(frame, (thumb_width, thumb_height))
            
            # Add timestamp and camera name overlay
            cv2.putText(thumbnail, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(thumbnail, camera_name, (10, thumb_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(thumbnail, "📹 CLIP", (thumb_width - 80, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
            # Save thumbnail
            success = cv2.imwrite(thumbnail_path, thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            return success
            
        except Exception as e:
            logger.error(f"❌ OpenCV frame extraction error: {e}")
            return False
    
    def _extract_frame_ffmpeg(self, video_path: str, thumbnail_path: str) -> bool:
        """Extract a frame using ffmpeg as fallback"""
        try:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vframes', '1',
                '-ss', '00:00:02',  # 2 seconds in
                '-vf', 'scale=320:-1',  # Scale to 320 width, preserve aspect ratio
                '-y',  # Overwrite output
                thumbnail_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and Path(thumbnail_path).exists():
                return True
            else:
                logger.warning(f"⚠️ ffmpeg extraction failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ ffmpeg extraction error: {e}")
            return False
    
    def _add_overlay_to_thumbnail(self, thumbnail_path: str, camera_name: str, timestamp: str):
        """Add text overlay to a thumbnail created by ffmpeg"""
        try:
            img = cv2.imread(thumbnail_path)
            if img is not None:
                height, width = img.shape[:2]
                
                # Add overlays
                cv2.putText(img, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(img, camera_name, (10, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(img, "📹 CLIP", (width - 80, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                
                cv2.imwrite(thumbnail_path, img, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
        except Exception as e:
            logger.error(f"❌ Error adding overlay to thumbnail: {e}")
    
    def _extract_metadata_from_filename(self, filename: str) -> Dict[str, str]:
        """Extract camera name and timestamp from video filename"""
        metadata = {'camera': 'unknown', 'timestamp': datetime.now().isoformat()}
        
        try:
            # Expected formats:
            # nest_20250115_143045_mot.mp4 (from RecordingEngine)
            # CritterCam_20250115_143045.mp4 (older format)
            # nutpod_motion_20250115_143045.avi (from old recording engine)
            
            name_without_ext = Path(filename).stem
            parts = name_without_ext.split('_')
            
            if len(parts) >= 3:
                # Try to identify camera name (first part)
                camera_part = parts[0].lower()
                if 'nest' in camera_part or 'bird' in camera_part:
                    metadata['camera'] = 'NestCam'
                elif 'crit' in camera_part or 'squirrel' in camera_part:
                    metadata['camera'] = 'CritterCam'
                else:
                    metadata['camera'] = parts[0].title()
                
                # Try to find timestamp (format: YYYYMMDD_HHMMSS or YYYYMMDDHHMMSS)
                for part in parts[1:]:
                    if len(part) == 8 and part.isdigit():
                        # Date part: YYYYMMDD
                        date_str = part
                        # Look for time part
                        time_idx = parts.index(part) + 1
                        if time_idx < len(parts) and len(parts[time_idx]) == 6 and parts[time_idx].isdigit():
                            time_str = parts[time_idx]
                            # Convert to ISO format
                            try:
                                dt = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
                                metadata['timestamp'] = dt.isoformat()
                                break
                            except ValueError:
                                pass
                    elif len(part) == 14 and part.isdigit():
                        # Combined date+time: YYYYMMDDHHMMSS
                        try:
                            dt = datetime.strptime(part, "%Y%m%d%H%M%S")
                            metadata['timestamp'] = dt.isoformat()
                            break
                        except ValueError:
                            pass
            
        except Exception as e:
            logger.warning(f"⚠️ Could not extract metadata from filename '{filename}': {e}")
        
        return metadata
    
    def create_thumbnail_for_clip(self, clip_path: str) -> Optional[str]:
        """
        Create a thumbnail for a clip and return the thumbnail path
        
        Args:
            clip_path: Path to the video clip file
            
        Returns:
            str: Path to the created thumbnail, or None if failed
        """
        return self.extract_thumbnail_from_video(clip_path)
    
    def get_thumbnail_for_sighting(self, clip_path: str, camera_name: str, timestamp: str) -> Optional[str]:
        """
        Get or create a thumbnail for a sighting
        
        Args:
            clip_path: Path to the video clip
            camera_name: Name of the camera
            timestamp: Timestamp of the sighting
            
        Returns:
            str: Path to the thumbnail file, or None if failed
        """
        # Check if thumbnail already exists
        safe_timestamp = timestamp.replace(':', '-').replace('T', '_').split('.')[0]
        thumbnail_filename = f"{camera_name}_{safe_timestamp}_clip.jpg"
        thumbnail_path = self.thumbnails_dir / thumbnail_filename
        
        if thumbnail_path.exists():
            logger.info(f"📸 Using existing thumbnail: {thumbnail_path}")
            return str(thumbnail_path)
        
        # Create new thumbnail
        return self.extract_thumbnail_from_video(clip_path, timestamp, camera_name)
    
    def cleanup_old_thumbnails(self, max_age_days: int = 30):
        """Remove thumbnails older than specified days"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_days * 24 * 60 * 60
            
            removed_count = 0
            for thumbnail_file in self.thumbnails_dir.glob("*.jpg"):
                file_age = current_time - thumbnail_file.stat().st_mtime
                if file_age > max_age_seconds:
                    thumbnail_file.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                logger.info(f"🧹 Cleaned up {removed_count} old thumbnails (older than {max_age_days} days)")
                
        except Exception as e:
            logger.error(f"❌ Error cleaning up old thumbnails: {e}")


# Global instance for easy access
video_thumbnail_extractor = VideoThumbnailExtractor()
