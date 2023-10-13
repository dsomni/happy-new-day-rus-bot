"""Contains the SecretsManager class instances"""

import os
import dotenv


class SecretsManager:
    """Manages secrets from .env file"""

    def __init__(self, path: str = os.path.join(".", ".env")) -> None:
        self._path = path
        self._secrets = dotenv.dotenv_values(self._path)
        self._bot_token: str = self._secrets["BOT_TOKEN"]  # type: ignore
        self._open_ai_token: str = self._secrets["OPENAI_TOKEN"]  # type: ignore
        self._hf_token: str = self._secrets["HUGGINGFACE_TOKEN"]  # type: ignore

    def get_bot_token(self) -> str:
        """Returns telegram bot token

        Returns:
            str: bot token
        """
        return self._bot_token

    def get_hf_token(self) -> str:
        """Returns Hugging Face access token

        Returns:
            str: Hugging Face  access token
        """
        return self._hf_token

    def get_open_ai_token(self) -> str:
        """Returns Open AI access token

        Returns:
            str: Open AI access token
        """
        return self._open_ai_token

    def set_open_ai_token(self, token: str):
        """Sets new Open AI access token

        Args:
            token (str)
        """
        dotenv.set_key(self._path, "OPENAI_TOKEN", token)
        self._open_ai_token = token


SECRETS_MANAGER = SecretsManager()
