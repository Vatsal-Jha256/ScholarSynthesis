"""
Configuration manager for LitReviewAgent
"""

import os
import json
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "llm": {
        "model_name": "meta-llama/Meta-Llama-3-8B-Instruct",
        "temperature": 0.1,
        "max_tokens": 1024
    },
    "search": {
        "api_key": None,  # Semantic Scholar API key
        "max_papers_per_query": 15,
        "max_search_iterations": 3
    },
    "analysis": {
        "relevance_threshold": 0.5,
        "duplicate_threshold": 0.8,
        "min_keywords": 5
    },
    "output": {
        "default_format": "markdown",  # markdown, latex, html
        "output_dir": "./output",
        "create_summary": True,
        "verbose_output": True
    },
    "caching": {
        "enabled": True,
        "cache_dir": "./.cache",
        "max_cache_age_days": 7
    }
}

class ConfigManager:
    """Manages configuration for LitReviewAgent"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize with configuration
        
        Args:
            config_path: Path to config file (None for default config)
        """
        self.config = DEFAULT_CONFIG.copy()
        self.config_path = config_path
        
        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)
    
    def load_from_file(self, config_path: str) -> None:
        """Load configuration from a file"""
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            
            # Update config with user values, preserving defaults for missing keys
            for section, values in user_config.items():
                if section in self.config:
                    if isinstance(values, dict):
                        self.config[section].update(values)
                    else:
                        self.config[section] = values
                else:
                    self.config[section] = values
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
    
    def save_to_file(self, config_path: Optional[str] = None) -> None:
        """Save configuration to a file"""
        path = config_path or self.config_path
        if not path:
            path = "config.json"
            
        try:
            with open(path, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.config_path = path
        except Exception as e:
            print(f"Error saving config to {path}: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        try:
            return self.config[section][key]
        except KeyError:
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set a configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get an entire configuration section"""
        return self.config.get(section, {})

# Helper functions for loading and saving configs
def load_config(config_path: str) -> ConfigManager:
    """Load configuration from a file"""
    return ConfigManager(config_path)

def save_config(config: ConfigManager, config_path: str) -> None:
    """Save configuration to a file"""
    config.save_to_file(config_path) 