from pydantic_settings import BaseSettings
from typing import Literal, Optional, Any
from langchain_openai import ChatOpenAI

class Settings(BaseSettings):
    ai_provider: Literal["openai", "minimax", "anthropic", "zhipuai", "ollama"] = "openai"

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"

    minimax_api_key: Optional[str] = None
    minimax_model: str = "MiniMax-M2.7"
    minimax_base_url: str = "https://api.minimax.chat/v1"

    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    zhipuai_api_key: Optional[str] = None
    zhipuai_model: str = "glm-4"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    temperature: float = 0.7

    class Config:
        env_file = ".env"

def create_llm(provider: str = None) -> Any:
    if provider is None:
        provider = Settings().ai_provider

    settings = Settings()

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model_name=settings.openai_model,
            temperature=settings.temperature
        )

    elif provider == "minimax":
        if not settings.minimax_api_key:
            raise ValueError("MiniMax API key not configured")
        return ChatOpenAI(
            api_key=settings.minimax_api_key,
            model_name=settings.minimax_model,
            base_url=settings.minimax_base_url,
            temperature=settings.temperature
        )

    elif provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("Please install langchain-anthropic: pip install langchain-anthropic")
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        return ChatAnthropic(
            api_key=settings.anthropic_api_key,
            model_name=settings.anthropic_model,
            temperature=settings.temperature
        )

    elif provider == "zhipuai":
        try:
            from langchain_community.chat_models import ChatZhipuAI
        except ImportError:
            raise ImportError("Please install langchain-community: pip install langchain-community")
        if not settings.zhipuai_api_key:
            raise ValueError("ZhipuAI API key not configured")
        return ChatZhipuAI(
            api_key=settings.zhipuai_api_key,
            model_name=settings.zhipuai_model,
            temperature=settings.temperature
        )

    elif provider == "ollama":
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=settings.temperature
        )

    else:
        raise ValueError(f"Unknown provider: {provider}")

settings = Settings()