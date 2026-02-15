from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    documents_dir: str = ""
    chroma_db_path: str = ""

    model_config = {"env_file": ".env"}


settings = Settings()
