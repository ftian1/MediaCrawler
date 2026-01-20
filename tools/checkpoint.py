# -*- coding: utf-8 -*-
# Copyright (c) 2025 relakkes@gmail.com
#
# This file is part of MediaCrawler project.
# Repository: https://github.com/NanmiCoder/MediaCrawler/blob/main/tools/checkpoint.py
# GitHub: https://github.com/NanmiCoder
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1
#

# 声明:本代码仅供学习和研究目的使用。使用者应遵守以下原则:
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率,避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

"""
Checkpoint module for crawler resume functionality (断点续传)
Provides functionality to save and restore crawler progress
"""

import json
import os
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path


# Try to import utils logger, fallback to standard logging if not available
try:
    from tools import utils
    logger = utils.logger
except ImportError:
    # Fallback to standard logging for testing and standalone usage
    import logging
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


class CheckpointManager:
    """
    Checkpoint Manager for crawler progress persistence
    
    Saves crawler state including:
    - Platform name
    - Current keyword being crawled
    - Last successfully crawled page number
    - Last crawled item ID
    - Timestamp of last update
    """
    
    def __init__(self, checkpoint_file: str = "data/checkpoint/crawler_checkpoint.json"):
        """
        Initialize checkpoint manager
        
        Args:
            checkpoint_file: Path to checkpoint file (relative or absolute)
        """
        # Convert to absolute path for better portability
        if not os.path.isabs(checkpoint_file):
            # Use current working directory as base for relative paths
            checkpoint_file = os.path.join(os.getcwd(), checkpoint_file)
        self.checkpoint_file = checkpoint_file
        self._ensure_directory()
    
    def _ensure_directory(self) -> None:
        """Ensure checkpoint directory exists"""
        checkpoint_dir = os.path.dirname(self.checkpoint_file)
        if checkpoint_dir and not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir, exist_ok=True)
    
    def save_checkpoint(
        self,
        platform: str,
        crawler_type: str,
        keyword: Optional[str] = None,
        last_page: Optional[int] = None,
        last_item_id: Optional[str] = None,
        creator_id: Optional[str] = None,
        extra_data: Optional[Dict] = None,
    ) -> None:
        """
        Save crawler checkpoint
        
        Args:
            platform: Platform name (xhs, dy, ks, bili, wb, tieba, zhihu)
            crawler_type: Crawler type (search, detail, creator)
            keyword: Current search keyword (for search type)
            last_page: Last successfully crawled page number
            last_item_id: Last successfully crawled item ID
            creator_id: Creator ID (for creator type)
            extra_data: Additional data to save
        """
        checkpoint_data = self._load_all_checkpoints()
        
        # Create checkpoint key
        checkpoint_key = self._get_checkpoint_key(platform, crawler_type, keyword, creator_id)
        
        # Build checkpoint entry
        checkpoint_entry = {
            "platform": platform,
            "crawler_type": crawler_type,
            "keyword": keyword,
            "creator_id": creator_id,
            "last_page": last_page,
            "last_item_id": last_item_id,
            "timestamp": datetime.now().isoformat(),
            "extra_data": extra_data or {},
        }
        
        checkpoint_data[checkpoint_key] = checkpoint_entry
        
        # Save to file
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            logger.info(
                f"[CheckpointManager] Checkpoint saved: {checkpoint_key}, "
                f"page={last_page}, item_id={last_item_id}"
            )
        except Exception as e:
            logger.error(f"[CheckpointManager] Failed to save checkpoint: {e}")
    
    def load_checkpoint(
        self,
        platform: str,
        crawler_type: str,
        keyword: Optional[str] = None,
        creator_id: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Load checkpoint for specific platform and keyword
        
        Args:
            platform: Platform name
            crawler_type: Crawler type
            keyword: Search keyword (for search type)
            creator_id: Creator ID (for creator type)
        
        Returns:
            Checkpoint data dictionary or None if not found
        """
        checkpoint_data = self._load_all_checkpoints()
        checkpoint_key = self._get_checkpoint_key(platform, crawler_type, keyword, creator_id)
        
        checkpoint = checkpoint_data.get(checkpoint_key)
        if checkpoint:
            logger.info(
                f"[CheckpointManager] Checkpoint loaded: {checkpoint_key}, "
                f"page={checkpoint.get('last_page')}, "
                f"item_id={checkpoint.get('last_item_id')}"
            )
        return checkpoint
    
    def clear_checkpoint(
        self,
        platform: str,
        crawler_type: str,
        keyword: Optional[str] = None,
        creator_id: Optional[str] = None,
    ) -> None:
        """
        Clear checkpoint for specific platform and keyword
        
        Args:
            platform: Platform name
            crawler_type: Crawler type
            keyword: Search keyword (for search type)
            creator_id: Creator ID (for creator type)
        """
        checkpoint_data = self._load_all_checkpoints()
        checkpoint_key = self._get_checkpoint_key(platform, crawler_type, keyword, creator_id)
        
        if checkpoint_key in checkpoint_data:
            del checkpoint_data[checkpoint_key]
            try:
                with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
                logger.info(f"[CheckpointManager] Checkpoint cleared: {checkpoint_key}")
            except Exception as e:
                logger.error(f"[CheckpointManager] Failed to clear checkpoint: {e}")
    
    def clear_all_checkpoints(self) -> None:
        """Clear all checkpoints"""
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
                logger.info("[CheckpointManager] All checkpoints cleared")
        except Exception as e:
            logger.error(f"[CheckpointManager] Failed to clear all checkpoints: {e}")
    
    def _load_all_checkpoints(self) -> Dict:
        """
        Load all checkpoints from file
        
        Returns:
            Dictionary of all checkpoints
        """
        if not os.path.exists(self.checkpoint_file):
            return {}
        
        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"[CheckpointManager] Invalid JSON in checkpoint file: {e}")
            return {}
        except (IOError, OSError) as e:
            logger.error(f"[CheckpointManager] Failed to read checkpoint file: {e}")
            return {}
        except Exception as e:
            logger.error(f"[CheckpointManager] Unexpected error loading checkpoints: {e}")
            return {}
    
    @staticmethod
    def _get_checkpoint_key(
        platform: str,
        crawler_type: str,
        keyword: Optional[str] = None,
        creator_id: Optional[str] = None,
    ) -> str:
        """
        Generate checkpoint key
        
        Args:
            platform: Platform name
            crawler_type: Crawler type
            keyword: Search keyword
            creator_id: Creator ID
        
        Returns:
            Checkpoint key string
        """
        if crawler_type == "search" and keyword:
            return f"{platform}_{crawler_type}_{keyword}"
        elif crawler_type == "creator" and creator_id:
            return f"{platform}_{crawler_type}_{creator_id}"
        else:
            return f"{platform}_{crawler_type}"
