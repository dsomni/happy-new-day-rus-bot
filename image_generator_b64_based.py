import time
import aiohttp
import asyncio
from deep_translator import GoogleTranslator
from tqdm import tqdm


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

    async def _fetch_b64_hash(self, pocket_id: str) -> str:
        entities_url = f"https://api.fusionbrain.ai/api/v1/text2image/generate/pockets/{pocket_id}/entities"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(entities_url) as response:
                    if response.status != 200:
                        return ""
                    response_json = await response.json()
                    return response_json["result"][0]["response"][0]

            except BaseException:  # pylint: disable=W0718
                return ""

    async def _check_generation_status(self, pocket_id: str) -> bool:
        max_attempts: int = 10
        sleep_period_seconds: float = 6

        status_url = f"https://api.fusionbrain.ai/api/v1/text2image/generate/pockets/{pocket_id}/status"

        async with aiohttp.ClientSession() as session:
            for _ in range(max_attempts):
                try:
                    async with session.get(status_url) as response:
                        response_json = await response.json()
                        if response_json["result"] == "SUCCESS":
                            return True
                    await asyncio.sleep(sleep_period_seconds)

                except BaseException:  # pylint: disable=W0718
                    return False

        return False

    def _prepare_prompt(self, prompt: str) -> str:
        fixed_prompt = prompt.replace("«", "'").replace("»", "'")
        # translated to en images are more precise
        return self.translator.translate(fixed_prompt)

    async def _api_request(self, prompt: str) -> tuple[str, int]:
        """Request to Fusion Brain api

        Args:
            prompt (str): image prompt

        Returns:
            tuple[str, int]: (image_b64, number_of_requests_made)
        """

        requests_number = 0
        try:
            form_data = aiohttp.FormData()
            form_data.add_field("queueType", "generate")
            form_data.add_field("query", self._prepare_prompt(prompt))
            form_data.add_field("preset", 1)
            form_data.add_field("style", "")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.url, headers=self.headers, data=form_data
                ) as response:
                    requests_number += 1

                    if not response.ok:
                        return ("", requests_number)
                    response_json = await response.json()

            pocket_id = response_json["result"]["pocketId"]

            succeeded = await self._check_generation_status(pocket_id)

            if not succeeded:
                return ("", requests_number)

            return (await self._fetch_b64_hash(pocket_id), requests_number)

        except BaseException:  # pylint: disable=W0718
            pass
        return ("", requests_number)

    def __init__(self) -> None:
        super().__init__()

        self.max_rate_per_minute = 5
        self.request_delay_seconds = (60 / self.max_rate_per_minute) + 1

        self.url = "https://api.fusionbrain.ai/api/v1/text2image/run"
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
        for i, prompt in tqdm(
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
