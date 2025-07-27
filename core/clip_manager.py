# clip_manager.py
"""
Nutflix Lite - Clip Management System

Handles video clip file management, metadata storage, and retention policies.
Provides organization by camera, date, and trigger type with FIFO cleanup.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import shutil
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ClipInfo:
    """Information about a video clip"""
    filename: str
    camera_id: str
    timestamp: datetime
    duration: float
    trigger_type: str
    ir_used: bool
    file_size: int
    metadata_file: Optional[str] = None

class ClipManager:
    """Manages video clip files, metadata, and retention policies"""
    
    def __init__(self, settings_manager=None):
        self.settings = settings_manager
        self.clip_settings = self._get_clip_settings()
        
        # Ensure storage directories exist
        self.storage_path = Path(self.clip_settings.get('storage_path', './clips'))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for organization
        self.cameras_path = self.storage_path / 'cameras'
        self.cameras_path.mkdir(exist_ok=True)
        
        logger.info(f"📁 ClipManager initialized - Storage: {self.storage_path}")
    
    def organize_clip(self, clip_filename: str, metadata: Dict[str, Any]) -> Tuple[str, str]:
        """
        Organize clip into camera-specific subdirectory
        
        Args:
            clip_filename: Original clip filename
            metadata: Clip metadata dictionary
            
        Returns:
            Tuple of (organized_clip_path, organized_metadata_path)
        """
        try:
            camera_id = metadata.get('camera_id', 'unknown')
            timestamp = datetime.fromisoformat(metadata.get('start_time', datetime.now().isoformat()))
            
            # Create camera subdirectory
            camera_dir = self.cameras_path / camera_id.lower()
            camera_dir.mkdir(exist_ok=True)
            
            # Create date subdirectory (YYYY-MM-DD)
            date_dir = camera_dir / timestamp.strftime('%Y-%m-%d')
            date_dir.mkdir(exist_ok=True)
            
            # Generate organized filename
            clip_basename = Path(clip_filename).name
            organized_clip = date_dir / clip_basename
            
            # Move clip file
            if Path(clip_filename).exists():
                shutil.move(clip_filename, organized_clip)
                logger.info(f"📁 Moved clip: {clip_basename} → {organized_clip}")
            
            # Move metadata file if it exists
            metadata_filename = clip_filename + ".json"
            organized_metadata = str(organized_clip) + ".json"
            
            if Path(metadata_filename).exists():
                shutil.move(metadata_filename, organized_metadata)
                logger.info(f"📁 Moved metadata: {Path(metadata_filename).name} → {organized_metadata}")
            else:
                # Create metadata in organized location
                with open(organized_metadata, 'w') as f:
                    json.dump(metadata, f, indent=2)
                logger.info(f"📁 Created metadata: {organized_metadata}")
            
            return str(organized_clip), organized_metadata
            
        except Exception as e:
            logger.error(f"❌ Failed to organize clip {clip_filename}: {e}")
            return clip_filename, clip_filename + ".json"
    
    def scan_clips(self, camera_id: Optional[str] = None, days_back: int = 30) -> List[ClipInfo]:
        """
        Scan storage directory for clips
        
        Args:
            camera_id: Filter by specific camera (None for all)
            days_back: How many days back to scan
            
        Returns:
            List of ClipInfo objects
        """
        clips = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        try:
            search_paths = []
            
            if camera_id:
                camera_dir = self.cameras_path / camera_id.lower()
                if camera_dir.exists():
                    search_paths.append(camera_dir)
            else:
                # Search all camera directories
                for camera_dir in self.cameras_path.iterdir():
                    if camera_dir.is_dir():
                        search_paths.append(camera_dir)
            
            # Also search root storage path for unorganized clips
            search_paths.append(self.storage_path)
            
            for search_path in search_paths:
                for clip_file in search_path.rglob('*.mp4'):
                    try:
                        clip_info = self._analyze_clip_file(clip_file, cutoff_date)
                        if clip_info:
                            clips.append(clip_info)
                    except Exception as e:
                        logger.warning(f"⚠️ Error analyzing clip {clip_file}: {e}")
                
                # Also check for mock clips in development
                for clip_file in search_path.rglob('*.mock'):
                    try:
                        clip_info = self._analyze_clip_file(clip_file, cutoff_date)
                        if clip_info:
                            clips.append(clip_info)
                    except Exception as e:
                        logger.warning(f"⚠️ Error analyzing mock clip {clip_file}: {e}")
            
            # Sort by timestamp (newest first)
            clips.sort(key=lambda x: x.timestamp, reverse=True)
            
            logger.info(f"📊 Found {len(clips)} clips" + (f" for {camera_id}" if camera_id else ""))
            return clips
            
        except Exception as e:
            logger.error(f"❌ Error scanning clips: {e}")
            return []
    
    def _analyze_clip_file(self, clip_file: Path, cutoff_date: datetime) -> Optional[ClipInfo]:
        """Analyze a single clip file and return ClipInfo"""
        try:
            # Get file stats
            stat = clip_file.stat()
            file_mtime = datetime.fromtimestamp(stat.st_mtime)
            
            # Skip files older than cutoff
            if file_mtime < cutoff_date:
                return None
            
            # Try to load metadata
            metadata_file = clip_file.with_suffix(clip_file.suffix + '.json')
            metadata = {}
            
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to read metadata for {clip_file}: {e}")
            
            # Extract info from filename if metadata is missing
            filename_parts = clip_file.stem.split('_')
            
            # Parse camera ID
            camera_id = metadata.get('camera_id')
            if not camera_id and len(filename_parts) >= 1:
                camera_short = filename_parts[0]
                camera_id = 'NestCam' if camera_short.startswith('nest') else 'CritterCam'
            
            # Parse timestamp
            timestamp = file_mtime
            if metadata.get('start_time'):
                try:
                    timestamp = datetime.fromisoformat(metadata['start_time'])
                except:
                    pass
            elif len(filename_parts) >= 2:
                try:
                    timestamp = datetime.strptime(filename_parts[1], '%Y%m%d_%H%M%S')
                except:
                    pass
            
            # Other metadata
            duration = metadata.get('duration', 10.0)
            trigger_type = metadata.get('trigger_type', 'unknown')
            ir_used = metadata.get('ir_used', False)
            
            return ClipInfo(
                filename=str(clip_file),
                camera_id=camera_id or 'unknown',
                timestamp=timestamp,
                duration=duration,
                trigger_type=trigger_type,
                ir_used=ir_used,
                file_size=stat.st_size,
                metadata_file=str(metadata_file) if metadata_file.exists() else None
            )
            
        except Exception as e:
            logger.error(f"❌ Error analyzing clip file {clip_file}: {e}")
            return None
    
    def cleanup_old_clips(self, max_clips: Optional[int] = None, max_age_days: Optional[int] = None) -> Dict[str, int]:
        """
        Clean up old clips based on retention policy
        
        Args:
            max_clips: Maximum number of clips per camera (FIFO)
            max_age_days: Maximum age in days
            
        Returns:
            Dictionary with cleanup statistics
        """
        stats = {'files_deleted': 0, 'bytes_freed': 0, 'cameras_processed': 0}
        
        try:
            # Get settings
            if max_clips is None:
                max_clips = self.clip_settings.get('max_clips', 100)
            if max_age_days is None:
                max_age_days = self.clip_settings.get('max_age_days', 30)
            
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            # Process each camera directory
            for camera_dir in self.cameras_path.iterdir():
                if not camera_dir.is_dir():
                    continue
                
                camera_id = camera_dir.name
                stats['cameras_processed'] += 1
                
                # Get all clips for this camera
                clips = []
                for clip_file in camera_dir.rglob('*.mp4'):
                    try:  
                        stat = clip_file.stat()
                        clips.append((clip_file, datetime.fromtimestamp(stat.st_mtime), stat.st_size))
                    except:
                        continue
                
                # Also check mock clips
                for clip_file in camera_dir.rglob('*.mock'):
                    try:
                        stat = clip_file.stat()
                        clips.append((clip_file, datetime.fromtimestamp(stat.st_mtime), stat.st_size))
                    except:
                        continue
                
                # Sort by timestamp (oldest first for deletion)
                clips.sort(key=lambda x: x[1])
                
                # Delete clips that are too old
                for clip_file, timestamp, file_size in clips:
                    if timestamp < cutoff_date:
                        self._delete_clip_and_metadata(clip_file, file_size, stats)
                
                # Refresh clip list after age-based deletion
                remaining_clips = [(f, t, s) for f, t, s in clips if t >= cutoff_date]
                
                # Delete excess clips (FIFO)
                if len(remaining_clips) > max_clips:
                    excess_clips = remaining_clips[:-max_clips]  # Keep the newest max_clips
                    for clip_file, timestamp, file_size in excess_clips:
                        self._delete_clip_and_metadata(clip_file, file_size, stats)
            
            logger.info(f"🧹 Cleanup complete: {stats['files_deleted']} files deleted, "
                       f"{stats['bytes_freed']/1024/1024:.1f} MB freed, "
                       f"{stats['cameras_processed']} cameras processed")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
            return stats
    
    def _delete_clip_and_metadata(self, clip_file: Path, file_size: int, stats: Dict[str, int]):
        """Delete a clip file and its associated metadata"""
        try:
            # Delete metadata file if it exists
            metadata_file = clip_file.with_suffix(clip_file.suffix + '.json')
            if metadata_file.exists():
                metadata_file.unlink()
                stats['files_deleted'] += 1
            
            # Delete clip file
            clip_file.unlink()
            stats['files_deleted'] += 1
            stats['bytes_freed'] += file_size
            
            logger.debug(f"🗑️ Deleted: {clip_file.name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to delete {clip_file}: {e}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        try:
            total_size = 0
            clip_count = 0
            camera_stats = defaultdict(lambda: {'count': 0, 'size': 0})
            
            # Scan all clip files
            for clip_file in self.storage_path.rglob('*.mp4'):
                try:
                    stat = clip_file.stat()
                    total_size += stat.st_size
                    clip_count += 1
                    
                    # Determine camera from path
                    camera_id = 'unknown'
                    if 'cameras' in clip_file.parts:
                        camera_idx = clip_file.parts.index('cameras')
                        if camera_idx + 1 < len(clip_file.parts):
                            camera_id = clip_file.parts[camera_idx + 1]
                    
                    camera_stats[camera_id]['count'] += 1
                    camera_stats[camera_id]['size'] += stat.st_size
                    
                except:
                    continue
            
            # Also count mock files in development
            for clip_file in self.storage_path.rglob('*.mock'):
                try:
                    stat = clip_file.stat()
                    total_size += stat.st_size
                    clip_count += 1
                    
                    camera_id = 'mock'
                    camera_stats[camera_id]['count'] += 1
                    camera_stats[camera_id]['size'] += stat.st_size
                except:
                    continue
            
            return {
                'total_clips': clip_count,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / 1024 / 1024,
                'storage_path': str(self.storage_path),
                'camera_breakdown': dict(camera_stats)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting storage stats: {e}")
            return {'error': str(e)}
    
    def _get_clip_settings(self) -> Dict[str, Any]:
        """Get clip management settings"""
        if self.settings:
            try:
                return self.settings.get('clip_settings', {})
            except:
                pass
        
        return {
            'storage_path': './clips',
            'max_clips': 100,
            'max_age_days': 30,
            'organize_by_camera': True,
            'organize_by_date': True
        }
