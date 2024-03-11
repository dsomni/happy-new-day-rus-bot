import base64
import json
import random
import time
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
        return random.choice([*SETTINGS_MANAGER.image_generator.styles, ""])

    def _api_request(self, url: str, prompt: str) -> bytes:
        """Request to Hugging face api

        Args:
            url (str): string
            prompt (str): string

        Returns:
            str: uuid of result
        """

        parts = self.model_attempts - 1
        for i in range(self.model_attempts):
            try:
                if i == parts:
                    model_input = SETTINGS_MANAGER.get_image_soft_prompt()
                else:
                    model_input = self._prepare_prompt(prompt)
                response = requests.post(
                    url,
                    headers=self.headers,
                    json={
                        "inputs": model_input,
                    },
                    timeout=self.timeout,
                )
                if response.ok:
                    return base64.b64encode(response.content)

                if i == parts:
                    break
                try:
                    wait_time = (
                        float(
                            json.loads(
                                response.content.decode("utf8").replace("'", '"')
                            )["estimated_time"]
                        )
                        / parts
                    )

                    time.sleep(wait_time)
                except BaseException:  # pylint: disable=W0718
                    break

            except BaseException:  # pylint: disable=W0718
                pass
        return bytes([])

    def _api_wrapper(self, prompt: str, idx: int = 0) -> bytes:
        """Wraps request to Fusion Brain api

        Args:
            prompt (str): image prompt
            idx (int): image idx

        Returns:
            str, : image_b64
        """

        style = self._get_image_style()

        model = self.models_dict.get(style, None)

        if model is None:
            # model = self.basic_model
            model = self.basic_models[idx % len(self.basic_models)]

            if style != "":
                prompt = f"{prompt} in style '{style}'"

        return self._api_request(self.api_url + model, prompt)

    def __init__(self) -> None:
        super().__init__()

        self.api_url = "https://api-inference.huggingface.co/models/"

        self.basic_models = [
            "stabilityai/stable-diffusion-xl-base-1.0",
            "prompthero/openjourney",
            "runwayml/stable-diffusion-v1-5",
            "nitrosocke/Arcane-Diffusion",
            "digiplay/DucHaiten-Real3D-NSFW-V1",
        ]

        self.models_dict = dict(
            {
                "PIXELART": "nerijs/pixel-art-xl",
                "ANIME": "Linaqruf/animagine-xl",
                "REALISTIC1": "digiplay/AbsoluteReality_v1.8.1",
                "REALISTIC2": "Yntec/epiCPhotoGasm",
                "INKPUNK": "Envvi/Inkpunk-Diffusion",
                "HUM": "Yntec/humu",
                "CARTOON": "Yntec/sexyToons",
                "PORN": "stablediffusionapi/vr-porn",
                "IKEA": "ostris/ikea-instructions-lora-sdxl",
            }
        )

        self.timeout = 60

        self.headers = {"Authorization": f"Bearer {SECRETS_MANAGER.get_hf_token()}"}
        self.translator = GoogleTranslator(source="auto", target="en")

        self.attempt_rounds = 10
        self.model_attempts = 3

        self.delay_s = 0.3

    def get_image_b64_hash(self, prompt):
        return self._api_wrapper(prompt)

    def get_image_b64_hashes(self, prompts: list[str]) -> list[bytes]:

        prompt_hash_dict: dict[str, bytes] = dict()
        for prompt in prompts:
            prompt_hash_dict[prompt] = bytes([])

        remain_prompts = prompts.copy()

        for k in range(self.attempt_rounds):
            if len(remain_prompts) == 0:
                break

            running_prompts = remain_prompts.copy()
            remain_prompts = []

            for i, prompt in LOGGER.get_tqdm(
                enumerate(running_prompts),
                total=len(running_prompts),
                desc=f"Generating images (round {k+1})",
            ):
                b64_hash = self._api_wrapper(prompt, i)
                if not b64_hash:
                    remain_prompts.append(b64_hash)
                    continue

                prompt_hash_dict[prompt] = b64_hash
                time.sleep(self.delay_s)

        return [prompt_hash_dict[prompt] for prompt in prompts]
