import json
import random
import time
from typing import Optional
import aiohttp
import asyncio
from deep_translator import GoogleTranslator
from logger import LOGGER

from settings import SETTINGS_MANAGER


class AsyncB64BasedImageGeneratorInterface:
    """Asynchronous image generator Interface"""

    async def get_image_b64_hash(self, prompt: str) -> str:
        """Returns image base64 hash based on the prompt

        Args:
            prompt (str): image description

        Returns:
            str: image b64 hash
        """
        raise NotImplementedError

    async def get_image_b64_hashes(self, prompts: list[str]) -> list[str]:
        """Returns image b64 hashes based on the prompts

        Args:
            prompts (list[str]): image descriptions

        Returns:
            list[str]: image b64 hashes
        """
        raise NotImplementedError


class FusionBrainImageGenerator(AsyncB64BasedImageGeneratorInterface):
    """Asynchronous image generator based on Fusion Brain"""

    async def _check_generation_status(self, result_uuid: str) -> Optional[dict]:
        max_attempts: int = 40
        sleep_period_seconds: float = 3

        status_url = (
            f"https://api.fusionbrain.ai/web/api/v1/text2image/status/{result_uuid}"
        )

        async with aiohttp.ClientSession() as session:
            for _ in range(max_attempts):
                try:
                    async with session.get(status_url) as response:
                        response_json = await response.json()
                        if response_json["status"] == "DONE":
                            return response_json
                    await asyncio.sleep(sleep_period_seconds)

                except BaseException:  # pylint: disable=W0718
                    return None

        return None

    def _prepare_prompt(self, prompt: str) -> str:
        fixed_prompt = prompt.replace("«", "'").replace("»", "'")
        if SETTINGS_MANAGER.image_generator.should_translate_prompt:
            # translated to en images are more precise
            return self.translator.translate(fixed_prompt)
        return fixed_prompt

    def _get_image_style(self) -> str:
        return random.choice(SETTINGS_MANAGER.image_generator.styles)

    async def _api_request(self, prompt: str) -> tuple[str, int]:
        """Request to Fusion Brain api

        Args:
            prompt (str): image prompt

        Returns:
            tuple[str, int]: (image_b64, number_of_requests_made)
        """

        dumped_parameters = json.dumps(
            {
                "type": "GENERATE",
                "generateParams": {"query": self._prepare_prompt(prompt)},
                "width": self.image_width,
                "height": self.image_height,
                "style": self._get_image_style(),
            }
        )

        requests_number = 0
        try:
            form_data = aiohttp.FormData()
            form_data.add_field(
                "params",
                dumped_parameters,
                filename="blob",
                content_type="application/json",
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url, headers=self.headers, data=form_data
                ) as response:
                    requests_number += 1

                    if not response.ok:
                        return ("", requests_number)
                    start_response_json = await response.json()

            result_uuid = start_response_json["uuid"]

            result_dict = await self._check_generation_status(result_uuid)

            if result_dict is None:
                return ("", requests_number)

            return (result_dict["images"][0], requests_number)

        except BaseException:  # pylint: disable=W0718
            pass
        return ("", requests_number)

    def __init__(self) -> None:
        super().__init__()

        self.max_rate_per_minute = 5
        self.request_delay_seconds = (60 / self.max_rate_per_minute) + 1

        self.image_height = 512
        self.image_width = 512

        self.url = "https://api.fusionbrain.ai/web/api/v1/text2image/run?model_id=1"
        self.headers = {
            "Host": "api.fusionbrain.ai",
            "Origin": "https://editor.fusionbrain.ai",
        }
        self.translator = GoogleTranslator(source="auto", target="en")

    async def get_image_b64_hash(self, prompt):
        return await self._api_request(prompt)

    async def get_image_b64_hashes(self, prompts) -> list[str]:
        b64_hashes: list[str] = []
        total_prompts = len(prompts)
        for i, prompt in LOGGER.get_tqdm(
            enumerate(prompts),
            total=len(prompts),
            desc="Generating images",
        ):
            start_time = time.time()
            b64_hash, requests_number = await self._api_request(prompt)
            b64_hashes.append(b64_hash)

            if i != total_prompts - 1:
                end_time = time.time()

                delay = requests_number * self.request_delay_seconds - (
                    end_time - start_time
                )

                await asyncio.sleep(max(0, delay))

        return b64_hashes
