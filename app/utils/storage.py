"""
Persistent storage utility using JSON files with in-memory fallback for serverless
"""
import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class JSONStorage:
    """JSON-based storage with in-memory fallback for read-only file systems"""
    
    def __init__(self, storage_dir: str = "storage"):
        """
        Initialize JSON storage
        
        Args:
            storage_dir: Directory to store JSON files
        """
        self.storage_dir = Path(storage_dir)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.is_readonly = False
        
        # Try to create directory, if fails, use memory-only mode
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            # Test if we can write
            test_file = self.storage_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            logger.info(f"Initialized JSON storage at: {self.storage_dir.absolute()}")
        except (OSError, PermissionError) as e:
            self.is_readonly = True
            logger.warning(f"File system is read-only, using memory-only storage: {e}")
            # Try to load existing data if available
            self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing data files into memory if available"""
        try:
            if self.storage_dir.exists():
                for json_file in self.storage_dir.glob("*.json"):
                    store_name = json_file.stem
                    with open(json_file, 'r', encoding='utf-8') as f:
                        self.memory_cache[store_name] = json.load(f)
                    logger.info(f"Loaded {len(self.memory_cache[store_name])} items from '{store_name}' into memory")
        except Exception as e:
            logger.warning(f"Could not load existing data: {e}")
    
    def _get_file_path(self, store_name: str) -> Path:
        """Get file path for a store"""
        return self.storage_dir / f"{store_name}.json"
    
    def load_store(self, store_name: str) -> Dict[str, Any]:
        """
        Load data from JSON file or memory cache
        
        Args:
            store_name: Name of the store (e.g., 'syllabi', 'question_papers')
            
        Returns:
            Dictionary of stored data
        """
        # If in memory mode, return from cache
        if self.is_readonly:
            return self.memory_cache.get(store_name, {})
        
        file_path = self._get_file_path(store_name)
        
        if not file_path.exists():
            logger.info(f"Store '{store_name}' does not exist, returning empty dict")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} items from '{store_name}' store")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from '{store_name}': {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading '{store_name}': {e}", exc_info=True)
            return {}
    
    def save_store(self, store_name: str, data: Dict[str, Any]) -> bool:
        """
        Save data to JSON file or memory cache
        
        Args:
            store_name: Name of the store
            data: Dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        # If in memory mode, save to cache
        if self.is_readonly:
            self.memory_cache[store_name] = data
            logger.debug(f"Saved {len(data)} items to '{store_name}' memory cache")
            return True
        
        file_path = self._get_file_path(store_name)
        
        try:
            # Write to temporary file first
            temp_path = file_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            # Rename to actual file (atomic operation on most systems)
            temp_path.replace(file_path)
            logger.debug(f"Saved {len(data)} items to '{store_name}' store")
            return True
        except Exception as e:
            logger.error(f"Error saving '{store_name}': {e}", exc_info=True)
            # Fallback to memory
            self.memory_cache[store_name] = data
            logger.warning(f"Falling back to memory storage for '{store_name}'")
            return False
    
    def get_item(self, store_name: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a single item from store"""
        data = self.load_store(store_name)
        return data.get(item_id)
    
    def set_item(self, store_name: str, item_id: str, item_data: Dict[str, Any]) -> bool:
        """Set a single item in store"""
        data = self.load_store(store_name)
        data[item_id] = item_data
        return self.save_store(store_name, data)
    
    def delete_item(self, store_name: str, item_id: str) -> bool:
        """Delete a single item from store"""
        data = self.load_store(store_name)
        if item_id in data:
            del data[item_id]
            return self.save_store(store_name, data)
        return False
    
    def list_items(self, store_name: str) -> Dict[str, Any]:
        """List all items in store"""
        return self.load_store(store_name)
    
    def clear_store(self, store_name: str) -> bool:
        """Clear all items from store"""
        return self.save_store(store_name, {})


# Global storage instance
_storage_instance: Optional[JSONStorage] = None


def get_storage(storage_dir: str = "storage") -> JSONStorage:
    """Get or create global storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = JSONStorage(storage_dir)
    return _storage_instance
