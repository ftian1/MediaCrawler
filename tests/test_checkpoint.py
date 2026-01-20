# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

"""
Tests for checkpoint functionality
"""

import json
import os
import tempfile
import pytest
from pathlib import Path

from tools.checkpoint import CheckpointManager


@pytest.fixture
def temp_checkpoint_file():
    """Create a temporary checkpoint file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_file = f.name
    yield temp_file
    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)


@pytest.fixture
def checkpoint_manager(temp_checkpoint_file):
    """Create a CheckpointManager instance for testing"""
    return CheckpointManager(checkpoint_file=temp_checkpoint_file)


class TestCheckpointManager:
    """Test CheckpointManager functionality"""
    
    def test_save_and_load_checkpoint(self, checkpoint_manager):
        """Test saving and loading checkpoint"""
        # Save checkpoint
        checkpoint_manager.save_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword",
            last_page=5,
            last_item_id="test_note_123"
        )
        
        # Load checkpoint
        checkpoint = checkpoint_manager.load_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword"
        )
        
        assert checkpoint is not None
        assert checkpoint["platform"] == "xhs"
        assert checkpoint["crawler_type"] == "search"
        assert checkpoint["keyword"] == "test_keyword"
        assert checkpoint["last_page"] == 5
        assert checkpoint["last_item_id"] == "test_note_123"
        assert "timestamp" in checkpoint
    
    def test_load_nonexistent_checkpoint(self, checkpoint_manager):
        """Test loading a checkpoint that doesn't exist"""
        checkpoint = checkpoint_manager.load_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="nonexistent_keyword"
        )
        
        assert checkpoint is None
    
    def test_clear_checkpoint(self, checkpoint_manager):
        """Test clearing a specific checkpoint"""
        # Save checkpoint
        checkpoint_manager.save_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword",
            last_page=5,
            last_item_id="test_note_123"
        )
        
        # Verify it exists
        checkpoint = checkpoint_manager.load_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword"
        )
        assert checkpoint is not None
        
        # Clear checkpoint
        checkpoint_manager.clear_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword"
        )
        
        # Verify it's cleared
        checkpoint = checkpoint_manager.load_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword"
        )
        assert checkpoint is None
    
    def test_multiple_checkpoints(self, checkpoint_manager):
        """Test handling multiple checkpoints"""
        # Save multiple checkpoints
        checkpoint_manager.save_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="keyword1",
            last_page=3,
            last_item_id="note_1"
        )
        
        checkpoint_manager.save_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="keyword2",
            last_page=7,
            last_item_id="note_2"
        )
        
        checkpoint_manager.save_checkpoint(
            platform="dy",
            crawler_type="search",
            keyword="keyword1",
            last_page=2,
            last_item_id="video_1"
        )
        
        # Load and verify each checkpoint
        checkpoint1 = checkpoint_manager.load_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="keyword1"
        )
        assert checkpoint1["last_page"] == 3
        assert checkpoint1["last_item_id"] == "note_1"
        
        checkpoint2 = checkpoint_manager.load_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="keyword2"
        )
        assert checkpoint2["last_page"] == 7
        assert checkpoint2["last_item_id"] == "note_2"
        
        checkpoint3 = checkpoint_manager.load_checkpoint(
            platform="dy",
            crawler_type="search",
            keyword="keyword1"
        )
        assert checkpoint3["last_page"] == 2
        assert checkpoint3["last_item_id"] == "video_1"
    
    def test_creator_type_checkpoint(self, checkpoint_manager):
        """Test checkpoint for creator type"""
        checkpoint_manager.save_checkpoint(
            platform="xhs",
            crawler_type="creator",
            creator_id="user_123",
            last_page=4,
            last_item_id="note_456"
        )
        
        checkpoint = checkpoint_manager.load_checkpoint(
            platform="xhs",
            crawler_type="creator",
            creator_id="user_123"
        )
        
        assert checkpoint is not None
        assert checkpoint["creator_id"] == "user_123"
        assert checkpoint["last_page"] == 4
    
    def test_extra_data(self, checkpoint_manager):
        """Test saving extra data in checkpoint"""
        extra_data = {
            "search_id": "abc123",
            "custom_field": "custom_value"
        }
        
        checkpoint_manager.save_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword",
            last_page=5,
            last_item_id="test_note_123",
            extra_data=extra_data
        )
        
        checkpoint = checkpoint_manager.load_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword"
        )
        
        assert checkpoint["extra_data"]["search_id"] == "abc123"
        assert checkpoint["extra_data"]["custom_field"] == "custom_value"
    
    def test_update_checkpoint(self, checkpoint_manager):
        """Test updating an existing checkpoint"""
        # Save initial checkpoint
        checkpoint_manager.save_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword",
            last_page=5,
            last_item_id="note_1"
        )
        
        # Update checkpoint
        checkpoint_manager.save_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword",
            last_page=10,
            last_item_id="note_2"
        )
        
        # Verify updated values
        checkpoint = checkpoint_manager.load_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword"
        )
        
        assert checkpoint["last_page"] == 10
        assert checkpoint["last_item_id"] == "note_2"
    
    def test_clear_all_checkpoints(self, checkpoint_manager, temp_checkpoint_file):
        """Test clearing all checkpoints"""
        # Save multiple checkpoints
        checkpoint_manager.save_checkpoint(
            platform="xhs",
            crawler_type="search",
            keyword="keyword1",
            last_page=3
        )
        
        checkpoint_manager.save_checkpoint(
            platform="dy",
            crawler_type="search",
            keyword="keyword2",
            last_page=5
        )
        
        # Clear all checkpoints
        checkpoint_manager.clear_all_checkpoints()
        
        # Verify file is deleted
        assert not os.path.exists(temp_checkpoint_file)
    
    def test_checkpoint_key_generation(self):
        """Test checkpoint key generation"""
        # Test search type
        key1 = CheckpointManager._get_checkpoint_key(
            platform="xhs",
            crawler_type="search",
            keyword="test_keyword"
        )
        assert key1 == "xhs_search_test_keyword"
        
        # Test creator type
        key2 = CheckpointManager._get_checkpoint_key(
            platform="xhs",
            crawler_type="creator",
            creator_id="user_123"
        )
        assert key2 == "xhs_creator_user_123"
        
        # Test detail type
        key3 = CheckpointManager._get_checkpoint_key(
            platform="xhs",
            crawler_type="detail"
        )
        assert key3 == "xhs_detail"
