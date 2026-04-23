from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    debug_mode: bool = False
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "symmetry"
    ollama_host: str = "http://localhost:11434"
    
    # Reward System Constants
    custodian_email: str = "beysasj@gmail.com"
    airdrop_amount: float = 100.0
    airdrop_limit: int = 1000
    base_reward: float = 5.0
    min_read_time: float = 10.0



settings = Settings()
