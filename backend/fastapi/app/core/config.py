from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    debug_mode: bool = False
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "symmetry"
    
    # External Services
    ollama_host: str = "http://localhost:11434"
    
    # Kafka / Redpanda
    kafka_bootstrap_servers: str = "redpanda:9092"
    kafka_topic_raw: str = "raw_twitter_data"
    kafka_topic_processed: str = "processed_twitter_data"

    # Twitter API
    twitter_bearer_token: Optional[str] = None
    
    # Reward System Constants
    custodian_email: str = "beysasj@gmail.com"
    airdrop_amount: float = 100.0
    airdrop_limit: int = 1000
    base_reward: float = 5.0
    min_read_time: float = 10.0
    
    # Security
    secret_key: str = "supersymmetry-secret-key-change-in-prod"

settings = Settings()
