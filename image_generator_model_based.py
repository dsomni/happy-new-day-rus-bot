import base64
import json
import random
import time
from typing import Optional
import aiohttp
import asyncio
from deep_translator import GoogleTranslator
import requests
from local_secrets import SECRETS_MANAGER
from logger import LOGGER

from settings import SETTINGS_MANAGER


class ModelBasedImageGeneratorInterface:
    """Asynchronous image generator Interface"""

    async def get_image_b64_hash(self, prompt: str) -> bytes:
        """Returns image base64 hash based on the prompt

        Args:
            prompt (str): image description

        Returns:
            str: image b64 hash
        """
        raise NotImplementedError

    async def get_image_b64_hashes(self, prompts: list[str]) -> list[bytes]:
        """Returns image b64 hashes based on the prompts

        Args:
            prompts (list[str]): image descriptions

        Returns:
            list[str]: image b64 hashes
        """
        raise NotImplementedError


class HuggingFaceImageGenerator(ModelBasedImageGeneratorInterface):
    """Asynchronous image generator based on Fusion Brain"""

    def _prepare_prompt(self, prompt: str) -> str:
        fixed_prompt = prompt.replace("«", "'").replace("»", "'")
        return self.translator.translate(fixed_prompt)

    def _get_image_style(self) -> str:
        return random.choice(SETTINGS_MANAGER.image_generator.styles)

    def _api_request(self, url: str, prompt: str) -> bytes:
        """Request to Hugging face api

        Args:
            url (str): string
            prompt (str): string

        Returns:
            str: uuid of result
        """

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={
                    "inputs": self._prepare_prompt(prompt),
                },
                timeout=self.timeout,
            )
            if not response.ok:
                return bytes([])
            image_bytes = response.content
            return base64.b64encode(image_bytes)

        except BaseException:  # pylint: disable=W0718
            pass
        return bytes([])

    def _api_wrapper(self, prompt: str) -> bytes:
        """Wraps request to Fusion Brain api

        Args:
            prompt (str): image prompt

        Returns:
            str, : image_b64
        """

        style = self._get_image_style()

        model = self.basic_model
        if style == "PIXELART":
            model = self.pixel_art_model

        if style != "":
            prompt = f"{prompt} in style '{style}'"

        return self._api_request(self.api_url + model, prompt)

    def __init__(self) -> None:
        super().__init__()

        self.api_url = "https://api-inference.huggingface.co/models/"

        self.basic_model = "stabilityai/stable-diffusion-xl-base-1.0"
        self.pixel_art_model = "nerijs/pixel-art-xl"

        self.timeout = 20

        self.max_rate_per_minute = 2
        self.request_delay_seconds = (60 / self.max_rate_per_minute) + 1

        self.headers = {"Authorization": f"Bearer {SECRETS_MANAGER.get_hf_token()}"}
        self.translator = GoogleTranslator(source="auto", target="en")

    def get_image_b64_hash(self, prompt):
        return self._api_wrapper(prompt)

    def get_image_b64_hashes(self, prompts) -> list[bytes]:
        b64_hashes: list[bytes] = []
        total_prompts = len(prompts)
        for i, prompt in LOGGER.get_tqdm(
            enumerate(prompts),
            total=len(prompts),
            desc="Generating images",
        ):
            start_time = time.time()
            b64_hash = self._api_wrapper(prompt)
            b64_hashes.append(b64_hash)

            if i != total_prompts - 1:
                end_time = time.time()

                delay = self.request_delay_seconds - (end_time - start_time)

                time.sleep(max(0, delay))

        return b64_hashes
