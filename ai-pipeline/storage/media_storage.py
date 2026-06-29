"""
Media Storage Module for capturing and storing snapshots and video clips.
Handles local file storage for alert evidence.
"""

import cv2
import numpy as np
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Tuple
from collections import deque
import threading
import logging

logger = logging.getLogger(__name__)


class MediaStorage:
    """
    Manages storage of snapshots and video clips for alerts.
    
    Features:
    - Snapshot capture (single frame)
    - Clip recording (circular buffer of N seconds)
    - Automatic file naming with timestamps
    - Local filesystem storage
    """
    
    def __init__(
        self,
        storage_dir: str = "./data/media",
        snapshot_dir: str = "snapshots",
        clip_dir: str = "clips",
        clip_duration_seconds: float = 10.0,
        fps: float = 30.0
    ):
        """
        Initialize media storage.
        
        Args:
            storage_dir: Root directory for media storage
            snapshot_dir: Subdirectory for snapshots
            clip_dir: Subdirectory for clips
            clip_duration_seconds: Duration of clip buffer in seconds
            fps: Frames per second for clip recording
        """
        self.storage_dir = Path(storage_dir)
        self.snapshot_dir = self.storage_dir / snapshot_dir
        self.clip_dir = self.storage_dir / clip_dir
        self.clip_duration_seconds = clip_duration_seconds
        self.fps = fps
        self.buffer_size = int(clip_duration_seconds * fps)
        
        # Circular buffer for clip recording
        self.frame_buffer: deque = deque(maxlen=self.buffer_size)
        self.buffer_lock = threading.Lock()
        
        # Create directories
        self._create_directories()
        
        logger.info(f"MediaStorage initialized: storage_dir={storage_dir}, clip_duration={clip_duration_seconds}s")
    
    def _create_directories(self):
        """Create storage directories if they don't exist."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.clip_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage directories created: {self.storage_dir}")
    
    def add_frame(self, frame: np.ndarray):
        """
        Add a frame to the circular buffer for clip recording.
        
        Args:
            frame: Video frame (numpy array)
        """
        with self.buffer_lock:
            self.frame_buffer.append(frame.copy())
    
    def capture_snapshot(
        self,
        frame: np.ndarray,
        alert_id: str,
        bbox: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[str]:
        """
        Capture and save a snapshot image.
        
        Args:
            frame: Video frame
            alert_id: Alert identifier for filename
            bbox: Optional bounding box [x1, y1, x2, y2] to crop around
        
        Returns:
            Path to saved snapshot, or None if failed
        """
        try:
            # Crop to bbox if provided
            if bbox is not None:
                x1, y1, x2, y2 = bbox
                # Add padding (20% of bbox size)
                pad_x = int((x2 - x1) * 0.2)
                pad_y = int((y2 - y1) * 0.2)
                x1 = max(0, x1 - pad_x)
                y1 = max(0, y1 - pad_y)
                x2 = min(frame.shape[1], x2 + pad_x)
                y2 = min(frame.shape[0], y2 + pad_y)
                frame = frame[y1:y2, x1:x2]
            
            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{alert_id}_{timestamp}.jpg"
            filepath = self.snapshot_dir / filename
            
            # Save image
            cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
            
            logger.info(f"Snapshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to capture snapshot: {e}")
            return None
    
    def save_clip(self, alert_id: str) -> Optional[str]:
        """
        Save the current frame buffer as a video clip.
        
        Args:
            alert_id: Alert identifier for filename
        
        Returns:
            Path to saved clip, or None if failed
        """
        try:
            with self.buffer_lock:
                if len(self.frame_buffer) == 0:
                    logger.warning("Frame buffer is empty, cannot save clip")
                    return None
                
                # Get frames from buffer
                frames = list(self.frame_buffer)
            
            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"clip_{alert_id}_{timestamp}.mp4"
            filepath = self.clip_dir / filename
            
            # Get frame dimensions from first frame
            height, width = frames[0].shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(
                str(filepath),
                fourcc,
                self.fps,
                (width, height)
            )
            
            # Write frames
            for frame in frames:
                writer.write(frame)
            
            writer.release()
            
            logger.info(f"Clip saved: {filepath} ({len(frames)} frames)")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save clip: {e}")
            return None
    
    def capture_alert_media(
        self,
        frame: np.ndarray,
        alert_id: str,
        bbox: Optional[Tuple[int, int, int, int]] = None,
        save_clip: bool = True
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Capture both snapshot and clip for an alert.
        
        Args:
            frame: Current video frame
            alert_id: Alert identifier
            bbox: Optional bounding box for snapshot crop
            save_clip: Whether to save video clip
        
        Returns:
            Tuple of (snapshot_path, clip_path)
        """
        snapshot_path = self.capture_snapshot(frame, alert_id, bbox)
        
        clip_path = None
        if save_clip:
            clip_path = self.save_clip(alert_id)
        
        return snapshot_path, clip_path
    
    def cleanup_old_media(self, max_age_hours: int = 24):
        """
        Delete media files older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours before deletion
        """
        import time
        
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        
        deleted_count = 0
        
        for directory in [self.snapshot_dir, self.clip_dir]:
            for filepath in directory.glob("*"):
                if filepath.is_file():
                    file_age = now - filepath.stat().st_mtime
                    if file_age > max_age_seconds:
                        try:
                            filepath.unlink()
                            deleted_count += 1
                            logger.debug(f"Deleted old media: {filepath}")
                        except Exception as e:
                            logger.error(f"Failed to delete {filepath}: {e}")
        
        logger.info(f"Cleanup complete: deleted {deleted_count} files older than {max_age_hours}h")
    
    def get_storage_stats(self) -> dict:
        """
        Get statistics about stored media.
        
        Returns:
            Dictionary with storage statistics
        """
        snapshot_count = len(list(self.snapshot_dir.glob("*")))
        clip_count = len(list(self.clip_dir.glob("*")))
        
        snapshot_size = sum(f.stat().st_size for f in self.snapshot_dir.glob("*") if f.is_file())
        clip_size = sum(f.stat().st_size for f in self.clip_dir.glob("*") if f.is_file())
        
        return {
            "snapshot_count": snapshot_count,
            "clip_count": clip_count,
            "snapshot_size_bytes": snapshot_size,
            "clip_size_bytes": clip_size,
            "total_size_bytes": snapshot_size + clip_size,
            "storage_dir": str(self.storage_dir)
        }
