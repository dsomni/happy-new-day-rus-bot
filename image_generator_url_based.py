import time
import aiohttp
import asyncio
from deep_translator import GoogleTranslator
from tqdm import tqdm

from settings import SETTINGS_MANAGER


class AsyncURLBasedImageGeneratorInterface:
    """Asynchronous image generator Interface"""

    async def get_image_url(self, prompt: str) -> str:
        """Returns image url based on the prompt

        Args:
            prompt (str): image description

        Returns:
            str: image url
        """
        raise NotImplementedError

    async def get_image_urls(self, prompts: list[str]) -> list[str]:
        """Returns image urls based on the prompts

        Args:
            prompts (list[str]): image descriptions

        Returns:
            list[str]: image urls
        """
        raise NotImplementedError


class DALLeImageGenerator(AsyncURLBasedImageGeneratorInterface):
    """Asynchronous image generator based on OpenAI DALL-E"""

    def _prepare_prompt(self, prompt: str) -> str:
        fixed_prompt = prompt.replace("«", "'").replace("»", "'")
        return self.translator.translate(fixed_prompt)

    async def _api_request(self, prompt: str) -> tuple[str, int]:
        """Request to Open AI api

        Args:
            prompt (str): image prompt

        Returns:
            tuple[str, int]: (image_url, number_of_requests_made)
        """

        requests_number = 0
        try:
            data = f'{{"prompt": "{self._prepare_prompt(prompt)}","n":1,"size":"{self.image_size}x{self.image_size}"}}'

            response_status = 400
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url, headers=self.headers, data=data
                ) as response:
                    requests_number += 1
                    response_status = response.status

                    if response.status == 200:
                        response = await response.json()

                        return (response["data"][0]["url"], requests_number)

                # 400 means that prompt is inappropriate
                if response_status != 400:
                    return ("", requests_number)

                soft_data = f'{{"prompt": "{SETTINGS_MANAGER.image_generator.soft_prompt }","n":1,"size":"{self.image_size}x{self.image_size}"}}'

                await asyncio.sleep(self.request_delay_seconds)

                async with session.post(
                    self.url, headers=self.headers, data=soft_data
                ) as response:
                    requests_number += 1
                    if response.status == 200:
                        response = await response.json()

                        return (response["data"][0]["url"], requests_number)
        except BaseException:  # pylint: disable=W0718
            pass
        return ("", requests_number)

    def __init__(self, key: str, image_size: int = 512) -> None:
        super().__init__()
        self.key = key
        self.image_size = image_size

        self.max_rate_per_minute = 5
        self.request_delay_seconds = (60 / self.max_rate_per_minute) + 1

        self.url = "https://api.openai.com/v1/images/generations"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.key}",
        }
        self.translator = GoogleTranslator(source="auto", target="en")

    async def get_image_url(self, prompt):
        return await self._api_request(prompt)

    async def get_image_urls(self, prompts) -> list[str]:
        urls: list[str] = []
        total_prompts = len(prompts)
        for i, prompt in tqdm(
            enumerate(prompts),
            total=len(prompts),
            desc="Generating images",
        ):
            start_time = time.time()
            url, requests_number = await self._api_request(prompt)
            urls.append(url)

            if i != total_prompts - 1:
                end_time = time.time()

                delay = requests_number * self.request_delay_seconds - (
                    end_time - start_time
                )

                await asyncio.sleep(max(0, delay))

        return urls
