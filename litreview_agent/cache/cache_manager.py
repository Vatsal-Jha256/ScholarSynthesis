"""
Cache management for LitReviewAgent
"""

import os
import json
import time
import hashlib
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta

# Singleton cache manager instance
_CACHE_MANAGER = None

class CacheManager:
    """Manages cache for search results and LLM responses"""
    
    def __init__(self, cache_dir: str = "./.cache", enabled: bool = True, max_age_days: int = 7):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
            enabled: Whether caching is enabled
            max_age_days: Maximum age of cache entries in days
        """
        self.cache_dir = cache_dir
        self.enabled = enabled
        self.max_age_days = max_age_days
        
        # Create cache directory if it doesn't exist
        if self.enabled and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            
        # Create subdirectories for different types of caches
        self.search_cache_dir = os.path.join(cache_dir, "search")
        self.llm_cache_dir = os.path.join(cache_dir, "llm")
        
        if self.enabled:
            os.makedirs(self.search_cache_dir, exist_ok=True)
            os.makedirs(self.llm_cache_dir, exist_ok=True)
    
    def _get_cache_key(self, data: str) -> str:
        """Generate a cache key from input data"""
        return hashlib.md5(data.encode("utf-8")).hexdigest()
    
    def _get_cache_file_path(self, cache_type: str, cache_key: str) -> str:
        """Get the file path for a cache entry"""
        if cache_type == "search":
            return os.path.join(self.search_cache_dir, f"{cache_key}.json")
        elif cache_type == "llm":
            return os.path.join(self.llm_cache_dir, f"{cache_key}.json")
        else:
            raise ValueError(f"Unknown cache type: {cache_type}")
    
    def get_from_cache(self, cache_type: str, query: str) -> Optional[Any]:
        """
        Get data from cache if it exists and is not expired
        
        Args:
            cache_type: Type of cache (search, llm)
            query: Query string used to generate the cache key
            
        Returns:
            Cached data or None if not found or expired
        """
        if not self.enabled:
            return None
            
        cache_key = self._get_cache_key(query)
        cache_file = self._get_cache_file_path(cache_type, cache_key)
        
        if not os.path.exists(cache_file):
            return None
            
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                
            # Check if cache is expired
            timestamp = cache_data.get("timestamp", 0)
            current_time = time.time()
            max_age = self.max_age_days * 24 * 60 * 60  # Convert days to seconds
            
            if current_time - timestamp > max_age:
                # Cache is expired, remove it
                os.remove(cache_file)
                return None
                
            return cache_data.get("data")
        except Exception as e:
            print(f"Error reading cache file {cache_file}: {e}")
            return None
    
    def save_to_cache(self, cache_type: str, query: str, data: Any) -> None:
        """
        Save data to cache
        
        Args:
            cache_type: Type of cache (search, llm)
            query: Query string used to generate the cache key
            data: Data to cache
        """
        if not self.enabled:
            return
            
        cache_key = self._get_cache_key(query)
        cache_file = self._get_cache_file_path(cache_type, cache_key)
        
        try:
            cache_data = {
                "timestamp": time.time(),
                "query": query,
                "data": data
            }
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error writing to cache file {cache_file}: {e}")
    
    def clear_cache(self, cache_type: Optional[str] = None) -> None:
        """
        Clear cache files
        
        Args:
            cache_type: Type of cache to clear (search, llm), or None for all
        """
        if not self.enabled:
            return
            
        if cache_type is None or cache_type == "search":
            for file in os.listdir(self.search_cache_dir):
                try:
                    os.remove(os.path.join(self.search_cache_dir, file))
                except Exception as e:
                    print(f"Error removing cache file: {e}")
                    
        if cache_type is None or cache_type == "llm":
            for file in os.listdir(self.llm_cache_dir):
                try:
                    os.remove(os.path.join(self.llm_cache_dir, file))
                except Exception as e:
                    print(f"Error removing cache file: {e}")
    
    def cleanup_old_cache(self) -> None:
        """Remove expired cache entries"""
        if not self.enabled:
            return
            
        current_time = time.time()
        max_age = self.max_age_days * 24 * 60 * 60  # Convert days to seconds
        
        # Clean up search cache
        for file in os.listdir(self.search_cache_dir):
            file_path = os.path.join(self.search_cache_dir, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                
                timestamp = cache_data.get("timestamp", 0)
                if current_time - timestamp > max_age:
                    os.remove(file_path)
            except Exception:
                # If we can't read the file or it's invalid, remove it
                try:
                    os.remove(file_path)
                except Exception:
                    pass
        
        # Clean up LLM cache
        for file in os.listdir(self.llm_cache_dir):
            file_path = os.path.join(self.llm_cache_dir, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                
                timestamp = cache_data.get("timestamp", 0)
                if current_time - timestamp > max_age:
                    os.remove(file_path)
            except Exception:
                # If we can't read the file or it's invalid, remove it
                try:
                    os.remove(file_path)
                except Exception:
                    pass

# Get the singleton cache manager instance
def get_cache_manager(cache_dir: str = "./.cache", enabled: bool = True, max_age_days: int = 7) -> CacheManager:
    """Get the singleton cache manager instance"""
    global _CACHE_MANAGER
    if _CACHE_MANAGER is None:
        _CACHE_MANAGER = CacheManager(cache_dir, enabled, max_age_days)
    return _CACHE_MANAGER 