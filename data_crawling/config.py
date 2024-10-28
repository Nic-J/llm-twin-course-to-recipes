from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    logging_level: str = "debug"

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

    MONGO_DATABASE_HOST: str = (
        "mongodb://mongo1:30001,mongo2:30002,mongo3:30003/?replicaSet=my-replica-set"
    )
    MONGO_DATABASE_NAME: str = "crawl-data"

    # Optional LinkedIn credentials for scraping your profile
    LINKEDIN_USERNAME: str | None = None
    LINKEDIN_PASSWORD: str | None = None


settings = Settings()
