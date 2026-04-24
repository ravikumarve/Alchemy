"""
Configuration Management for ALCHEMY

Centralized configuration management using environment variables
and Pydantic settings for type safety and validation.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings have default values for development but should be
    overridden in production using environment variables.
    """

    # Application
    app_name: str = "ALCHEMY - Temporal Content Transmuter"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["*"]

    # Database
    database_url: str = "sqlite:///./alchemy.db"
    database_echo: bool = False

    # Processing
    max_file_size: int = 104857600  # 100MB
    timeout_seconds: int = 80
    retry_count: int = 3
    max_concurrent_jobs: int = 5

    # Time budgets (in seconds)
    time_budget_validate_file: float = 5.0
    time_budget_extract_content: float = 2.0
    time_budget_analyze_semantics: float = 30.0
    time_budget_structure_data: float = 20.0
    time_budget_filter_quality: float = 15.0
    time_budget_enrich_metadata: float = 5.0
    time_budget_generate_package: float = 3.0

    # Quality thresholds
    min_evergreen_score: float = 0.5
    min_confidence_score: float = 0.5
    min_chunk_length: int = 50

    # Storage
    raw_ore_dir: str = "raw_ore"
    processed_gold_dir: str = "processed_gold"
    logs_dir: str = "logs"

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    api_key_header: str = "X-API-Key"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings.

    This function can be used as a FastAPI dependency.

    Returns:
        Application settings
    """
    return settings


def validate_settings() -> bool:
    """
    Validate application settings.

    Returns:
        True if settings are valid, False otherwise
    """
    # Validate time budgets sum to less than total timeout
    total_time_budget = (
        settings.time_budget_validate_file +
        settings.time_budget_extract_content +
        settings.time_budget_analyze_semantics +
        settings.time_budget_structure_data +
        settings.time_budget_filter_quality +
        settings.time_budget_enrich_metadata +
        settings.time_budget_generate_package
    )

    if total_time_budget > settings.timeout_seconds:
        print(f"WARNING: Total time budget ({total_time_budget}s) exceeds timeout ({settings.timeout_seconds}s)")

    # Validate quality thresholds
    if not (0.0 <= settings.min_evergreen_score <= 1.0):
        print(f"ERROR: min_evergreen_score must be between 0.0 and 1.0")
        return False

    if not (0.0 <= settings.min_confidence_score <= 1.0):
        print(f"ERROR: min_confidence_score must be between 0.0 and 1.0")
        return False

    # Validate directories exist or can be created
    for dir_path in [settings.raw_ore_dir, settings.processed_gold_dir, settings.logs_dir]:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"Created directory: {dir_path}")
            except Exception as e:
                print(f"ERROR: Cannot create directory {dir_path}: {str(e)}")
                return False

    return True


if __name__ == "__main__":
    # Print current settings
    print("Current Application Settings:")
    print("=" * 50)
    for key, value in settings.dict().items():
        if "secret" not in key.lower() and "key" not in key.lower():
            print(f"{key}: {value}")
    print("=" * 50)

    # Validate settings
    if validate_settings():
        print("✓ Settings are valid")
    else:
        print("✗ Settings validation failed")
