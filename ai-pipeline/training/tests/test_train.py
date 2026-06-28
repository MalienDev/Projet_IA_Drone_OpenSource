"""
Unit tests for training module.
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_data_yaml_exists():
    """Test that data.yaml exists."""
    # Get project root (3 levels up from tests/)
    project_root = Path(__file__).parent.parent.parent.parent
    data_yaml = project_root / "datasets" / "dataset_merged" / "data.yaml"
    assert data_yaml.exists(), f"data.yaml not found at {data_yaml}"


def test_data_yaml_content():
    """Test that data.yaml has valid content."""
    project_root = Path(__file__).parent.parent.parent.parent
    data_yaml = project_root / "datasets" / "dataset_merged" / "data.yaml"
    with open(data_yaml, 'r') as f:
        content = f.read()
    
    assert "names:" in content
    assert "nc:" in content
    assert "path:" in content
    assert "train:" in content
    assert "val:" in content


def test_dataset_structure():
    """Test that dataset has correct structure."""
    project_root = Path(__file__).parent.parent.parent.parent
    base_path = project_root / "datasets" / "dataset_merged"
    
    # Check that train, val, test directories exist
    assert (base_path / "train" / "images").exists()
    assert (base_path / "train" / "labels").exists()
    assert (base_path / "val" / "images").exists()
    assert (base_path / "val" / "labels").exists()
    assert (base_path / "test" / "images").exists()
    assert (base_path / "test" / "labels").exists()
    
    # Check that directories are not empty
    assert len(list((base_path / "train" / "images").iterdir())) > 0
    assert len(list((base_path / "val" / "images").iterdir())) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
