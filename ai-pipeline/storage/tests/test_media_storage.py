"""
Tests for MediaStorage module.
"""

import pytest
import numpy as np
import cv2
from pathlib import Path
import tempfile
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from storage import MediaStorage


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for media storage tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_frame():
    """Create a sample video frame."""
    return np.ones((480, 640, 3), dtype=np.uint8) * 128


class TestMediaStorage:
    """Test suite for MediaStorage class."""
    
    def test_initialization(self, temp_storage_dir):
        """Test MediaStorage initialization."""
        storage = MediaStorage(storage_dir=temp_storage_dir)
        
        assert storage.storage_dir.exists()
        assert storage.snapshot_dir.exists()
        assert storage.clip_dir.exists()
    
    def test_add_frame(self, temp_storage_dir, sample_frame):
        """Test adding frames to buffer."""
        storage = MediaStorage(
            storage_dir=temp_storage_dir,
            clip_duration_seconds=1.0,
            fps=10.0
        )
        
        # Add frames
        for _ in range(5):
            storage.add_frame(sample_frame)
        
        assert len(storage.frame_buffer) == 5
    
    def test_buffer_overflow(self, temp_storage_dir, sample_frame):
        """Test circular buffer overflow."""
        storage = MediaStorage(
            storage_dir=temp_storage_dir,
            clip_duration_seconds=1.0,
            fps=5.0  # Buffer size = 5
        )
        
        # Add more frames than buffer size
        for _ in range(10):
            storage.add_frame(sample_frame)
        
        # Should only keep last 5 frames
        assert len(storage.frame_buffer) == 5
    
    def test_capture_snapshot(self, temp_storage_dir, sample_frame):
        """Test snapshot capture."""
        storage = MediaStorage(storage_dir=temp_storage_dir)
        
        snapshot_path = storage.capture_snapshot(sample_frame, "test-alert-123")
        
        assert snapshot_path is not None
        assert Path(snapshot_path).exists()
        assert "test-alert-123" in snapshot_path

    def test_to_public_path(self, temp_storage_dir, sample_frame):
        """Test converting a stored media file to a dashboard URL."""
        storage = MediaStorage(storage_dir=temp_storage_dir)

        snapshot_path = storage.capture_snapshot(sample_frame, "test-alert-123")
        public_path = storage.to_public_path(snapshot_path)

        assert public_path is not None
        assert public_path.startswith("/media/snapshots/")
        assert public_path.endswith(".jpg")
    
    def test_capture_snapshot_with_bbox(self, temp_storage_dir, sample_frame):
        """Test snapshot capture with bounding box crop."""
        storage = MediaStorage(storage_dir=temp_storage_dir)
        
        bbox = (100, 100, 300, 300)
        snapshot_path = storage.capture_snapshot(sample_frame, "test-alert-123", bbox)
        
        assert snapshot_path is not None
        assert Path(snapshot_path).exists()
        
        # Verify cropped image dimensions
        cropped = cv2.imread(snapshot_path)
        assert cropped.shape[0] <= sample_frame.shape[0]
        assert cropped.shape[1] <= sample_frame.shape[1]
    
    def test_save_clip(self, temp_storage_dir, sample_frame):
        """Test clip saving."""
        storage = MediaStorage(
            storage_dir=temp_storage_dir,
            clip_duration_seconds=1.0,
            fps=10.0
        )
        
        # Add frames to buffer
        for _ in range(10):
            storage.add_frame(sample_frame)
        
        clip_path = storage.save_clip("test-alert-123")
        
        assert clip_path is not None
        assert Path(clip_path).exists()
        assert "test-alert-123" in clip_path
        assert clip_path.endswith(".mp4")
    
    def test_save_clip_empty_buffer(self, temp_storage_dir):
        """Test clip saving with empty buffer."""
        storage = MediaStorage(storage_dir=temp_storage_dir)
        
        clip_path = storage.save_clip("test-alert-123")
        
        assert clip_path is None
    
    def test_capture_alert_media(self, temp_storage_dir, sample_frame):
        """Test capturing both snapshot and clip."""
        storage = MediaStorage(
            storage_dir=temp_storage_dir,
            clip_duration_seconds=1.0,
            fps=10.0
        )
        
        # Add frames to buffer
        for _ in range(10):
            storage.add_frame(sample_frame)
        
        snapshot_path, clip_path = storage.capture_alert_media(
            sample_frame,
            "test-alert-123",
            bbox=(100, 100, 300, 300)
        )
        
        assert snapshot_path is not None
        assert clip_path is not None
        assert Path(snapshot_path).exists()
        assert Path(clip_path).exists()
    
    def test_capture_alert_media_no_clip(self, temp_storage_dir, sample_frame):
        """Test capturing snapshot only (no clip)."""
        storage = MediaStorage(storage_dir=temp_storage_dir)
        
        snapshot_path, clip_path = storage.capture_alert_media(
            sample_frame,
            "test-alert-123",
            save_clip=False
        )
        
        assert snapshot_path is not None
        assert clip_path is None
    
    def test_get_storage_stats(self, temp_storage_dir, sample_frame):
        """Test storage statistics."""
        storage = MediaStorage(storage_dir=temp_storage_dir)
        
        # Create some files
        storage.capture_snapshot(sample_frame, "alert-1")
        storage.capture_snapshot(sample_frame, "alert-2")
        
        stats = storage.get_storage_stats()
        
        assert stats["snapshot_count"] == 2
        assert stats["clip_count"] == 0
        assert stats["storage_dir"] == temp_storage_dir
        assert stats["total_size_bytes"] > 0
    
    def test_cleanup_old_media(self, temp_storage_dir, sample_frame):
        """Test cleanup of old media files."""
        storage = MediaStorage(storage_dir=temp_storage_dir)
        
        # Create some files
        storage.capture_snapshot(sample_frame, "alert-1")
        storage.capture_snapshot(sample_frame, "alert-2")
        
        # Cleanup with max_age=0 (delete all)
        storage.cleanup_old_media(max_age_hours=0)
        
        stats = storage.get_storage_stats()
        assert stats["snapshot_count"] == 0
