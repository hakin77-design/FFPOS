"""Application configuration management."""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # API Keys
    football_api_key: str = ""
    rapidapi_key: str = ""
    sofascore_api_key: str = ""
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/matches.db"
    db_echo: bool = False
    
    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    cache_ttl: int = 3600
    
    # Application
    app_name: str = "FFPAS"
    app_version: str = "2.0.0"
    debug: bool = False
    port: int = 5000
    host: str = "0.0.0.0"
    
    # Model
    model_path: str = "ai_model.pt"
    model_version: str = "latest"
    batch_size: int = 32
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_max_size: int = 10485760  # 10MB
    log_backup_count: int = 5
    
    # Security
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    api_rate_limit: str = "100/minute"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Global settings instance
settings = Settings()
