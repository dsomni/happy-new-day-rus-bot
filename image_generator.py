import time
import aiohttp
import asyncio
from deep_translator import GoogleTranslator
from tqdm import tqdm

from settings import SETTINGS_MANAGER


class AsyncImageGeneratorInterface:
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


class DALLeImageGenerator(AsyncImageGeneratorInterface):
    """Asynchronous image generator based on OpenAI DALL-E"""

    def _prepare_prompt(self, prompt: str) -> str:
        fixed_prompt = prompt.replace("«", "'").replace("»", "'")
        return self.translator.translate(fixed_prompt)

    async def _api_request(self, prompt: str) -> str:
        try:
            data = f'{{"prompt": "{self._prepare_prompt(prompt)}","n":1,"size":"{self.image_size}x{self.image_size}"}}'

            response_status = 400
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url, headers=self.headers, data=data
                ) as response:
                    response_status = response.status

                    if response.status == 200:
                        response = await response.json()

                        return response["data"][0]["url"]

                # 400 means that prompt is inappropriate
                if response_status != 400:
                    return ""

                soft_data = f'{{"prompt": "{self.soft_prompt }","n":1,"size":"{self.image_size}x{self.image_size}"}}'

                async with session.post(
                    self.url, headers=self.headers, data=soft_data
                ) as response:
                    if response.status == 200:
                        response = await response.json()

                        return response["data"][0]["url"]
        except BaseException:  # pylint: disable=W0718
            pass
        return ""

    def __init__(self, key: str, image_size: int = 512) -> None:
        super().__init__()
        self.key = key
        self.image_size = image_size
        self.max_rate_per_minute = 5
        self.request_delay_seconds = 0.5
        self.url = "https://api.openai.com/v1/images/generations"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.key}",
        }
        self.translator = GoogleTranslator(source="auto", target="en")
        self.soft_prompt = SETTINGS_MANAGER.image_soft_prompt

    async def get_image_url(self, prompt):
        return await self._api_request(prompt)

    async def get_image_urls(self, prompts):
        batches = [
            prompts[i : i + self.max_rate_per_minute]
            for i in range(0, len(prompts), self.max_rate_per_minute)
        ]
        urls = []
        total_batches = len(batches)
        for i, batch in tqdm(
            enumerate(batches),
            total=len(batches),
            desc="Generating images (batches progress)",
        ):
            start_time = time.time()
            for prompt in batch:
                urls.append(await self._api_request(prompt))

                await asyncio.sleep(self.request_delay_seconds)
            if i != total_batches - 1:
                end_time = time.time()
                await asyncio.sleep(max(1, 61 - (end_time - start_time)))
        return urls
