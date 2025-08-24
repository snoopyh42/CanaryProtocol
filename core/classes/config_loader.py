#!/usr/bin/env python3
"""
Configuration Loader for Smart Canary Protocol
Loads and manages YAML configuration files with fallback to defaults
"""

import os
import yaml
from typing import Dict, Any


class ConfigLoader:
    _instance = None
    _config = None
    
    def __new__(cls, config_dir="config"):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance
    def __init__(self, config_dir="config"):
        if self._config is None:
            self.config_dir = config_dir
            self.defaults_file = os.path.join(config_dir, "config_defaults.yaml")
            self.user_config_file = os.path.join(config_dir, "config.yaml")
            self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration with user overrides falling back to defaults"""
        if self._config is not None:
            return self._config
            
        # Load defaults
        defaults = self._load_yaml_file(self.defaults_file)
        if not defaults:
            print(f"⚠️  Warning: Could not load default config from {self.defaults_file}")
            defaults = self._get_hardcoded_defaults()

        # Load user overrides if they exist
        user_config = {}
        if os.path.exists(self.user_config_file):
            user_config = self._load_yaml_file(self.user_config_file)
            if user_config:
                print(f"✅ Loaded user config from {self.user_config_file}")

        # Merge configurations (user overrides defaults)
        self._config = self._deep_merge(defaults, user_config)
        return self._config

    def _load_yaml_file(self, filepath: str) -> Dict[str, Any]:
        """Load a YAML file safely"""
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML file {filepath}: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error loading config file {filepath}: {e}")
            return {}

    def _deep_merge(self, base: Dict[str, Any],
                    override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries, with override taking precedence"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(
                    result[key],
                    dict) and isinstance(
                    value,
                    dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _get_hardcoded_defaults(self) -> Dict[str, Any]:
        """Fallback defaults if config files are missing"""
        return {
            "system": {
                "learning_enabled": True,
                "adaptation_rate": 0.1,
                "min_confidence_threshold": 0.6,
                "daily_collection_time": "08:00",
                "weekly_analysis_day": "sunday",
                "weekly_analysis_time": "09:00",
                "max_log_age_days": 90,
                "backup_frequency_days": 7,
                "urgent_analysis_score": 8.0,
                "critical_analysis_score": 9.0},
            "monitoring": {
                "news_sources": [
                    "https://feeds.npr.org/1001/rss.xml",
                    "https://rss.cnn.com/rss/edition.rss"],
                "economic_indicators": [
                    "VIX",
                    "GLD",
                    "DXY",
                    "BTC-USD"],
                "political_keywords": [
                    "election fraud",
                    "constitutional crisis",
                    "martial law"],
                "economic_keywords": [
                    "bank failures",
                    "hyperinflation",
                    "currency collapse"]},
            "notifications": {
                "send_daily_digest": False,
                "send_weekly_digest": True,
                "send_urgent_alerts": True},
            "intelligence": {
                "model": "gpt-4o",
                "temperature": 0.2,
                "max_tokens": 3000}}

    def get(self, key_path: str, default=None) -> Any:
        """Get configuration value using dot notation (e.g., 'system.learning_enabled')"""
        if not self._config:
            self.load_config()

        keys = key_path.split('.')
        value = self._config

        try:
            for key in keys:
                if value is None:
                    return default
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.get(section, {})

    def save_user_config(self, config: Dict[str, Any]) -> bool:
        """Save user configuration overrides"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.user_config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            print(f"✅ Saved user config to {self.user_config_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving user config: {e}")
            return False

    def create_example_user_config(self) -> bool:
        """Create an example user config file"""
        example_config = {
            "system": {
                "urgent_analysis_score": 7.5,  # Lower threshold
                "learning_enabled": True
            },
            "monitoring": {
                "news_sources": [
                    "https://feeds.npr.org/1001/rss.xml",
                    "https://rss.cnn.com/rss/edition.rss",
                    "https://feeds.reuters.com/Reuters/worldNews",
                    # "Add your preferred news sources here"
                ]
            },
            "notifications": {
                "send_daily_digest": False,
                "send_weekly_digest": True
            }
        }

        example_file = os.path.join(self.config_dir, "config_example.yaml")
        try:
            with open(example_file, 'w') as f:
                f.write("# Example user configuration for Smart Canary Protocol\n")
                f.write(
                    "# Copy this file to config.yaml and customize as needed\n\n")
                yaml.dump(
                    example_config,
                    f,
                    default_flow_style=False,
                    indent=2)
            print(f"✅ Created example config: {example_file}")
            return True
        except Exception as e:
            print(f"❌ Error creating example config: {e}")
            return False

    def reload(self):
        """Reload configuration from files"""
        self.load_config()

    def __str__(self) -> str:
        """String representation of current config"""
        if not self._config:
            return "Configuration not loaded"
        return yaml.dump(self._config, default_flow_style=False, indent=2)


# Global configuration instance
_config_loader = None


def get_config() -> ConfigLoader:
    """Get the global configuration loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader


def reload_config():
    """Reload the global configuration"""
    global _config_loader
    if _config_loader:
        _config_loader.reload()

# Convenience functions


def get_setting(key_path: str, default=None) -> Any:
    """Get a configuration setting using dot notation"""
    return get_config().get(key_path, default)


def get_section(section: str) -> Dict[str, Any]:
    """Get a configuration section"""
    return get_config().get_section(section)


if __name__ == "__main__":
    # Test the configuration loader
    config = ConfigLoader()
    print("🔧 Configuration Test")
    print("====================")
    print(f"Learning enabled: {config.get('system.learning_enabled')}")
    print(f"Urgent score threshold: {config.get('system.urgent_analysis_score')}")
    print(f"News sources: {len(config.get('monitoring.news_sources', []))}")
    print(f"Model: {config.get('intelligence.model')}")

    # Only create example if explicitly requested via command line argument
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "create-example":
        print("\n📝 Creating example user config...")
        config.create_example_user_config()
