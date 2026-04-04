"""Configuration Management Utility"""
import json
import os
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration from JSON files and environment variables"""
    
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._config:
            self.load_config()
    
    def load_config(self, environment: Optional[str] = None) -> None:
        """Load configuration from JSON file based on environment"""
        if environment is None:
            environment = os.getenv('ENVIRONMENT', 'dev')
        
        config_file = f"{environment}_app_config.json"
        config_path = Path(__file__).parent.parent.parent / "config" / config_file
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            self._config = json.load(f)
        
        # Replace environment variable placeholders
        self._replace_env_vars(self._config)
    
    def _replace_env_vars(self, config: Dict[str, Any]) -> None:
        """Recursively replace ${VAR_NAME} with environment variables"""
        for key, value in config.items():
            if isinstance(value, dict):
                self._replace_env_vars(value)
            elif isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                config[key] = os.getenv(env_var, value)
            elif isinstance(value, list):
                config[key] = [
                    os.getenv(item[2:-1], item) if isinstance(item, str) and item.startswith('${') else item
                    for item in value
                ]
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key (e.g., 'database.url')"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()
    
    @property
    def app_name(self) -> str:
        return self.get('app_name', 'FastAPI Auth Service')
    
    @property
    def version(self) -> str:
        return self.get('version', '1.0.0')
    
    @property
    def environment(self) -> str:
        return self.get('environment', 'development')
    
    @property
    def debug(self) -> bool:
        return self.get('debug', False)
    
    @property
    def database_url(self) -> str:
        return self.get('database.url', '')
    
    @property
    def jwt_secret_key(self) -> str:
        return self.get('jwt.secret_key', '')
    
    @property
    def jwt_algorithm(self) -> str:
        return self.get('jwt.algorithm', 'HS256')
    
    @property
    def jwt_access_token_expire_minutes(self) -> int:
        return self.get('jwt.access_token_expire_minutes', 30)
    
    @property
    def jwt_refresh_token_expire_days(self) -> int:
        return self.get('jwt.refresh_token_expire_days', 7)
    
    @property
    def redis_enabled(self) -> bool:
        return self.get('redis.enabled', True)
    
    @property
    def rate_limiting_enabled(self) -> bool:
        return self.get('rate_limiting.enabled', True)
    
    @property
    def razorpay_key_id(self) -> str:
        import os
        return os.getenv('RAZORPAY_KEY_ID', 'placeholder_key_id')
    
    @property
    def razorpay_key_secret(self) -> str:
        import os
        return os.getenv('RAZORPAY_KEY_SECRET', 'placeholder_key_secret')
    
    @property
    def razorpay_webhook_secret(self) -> str:
        import os
        return os.getenv('RAZORPAY_WEBHOOK_SECRET', 'placeholder_webhook_secret')


# Singleton instance
config = ConfigManager()
