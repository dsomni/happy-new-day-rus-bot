"""Contains Holiday class"""

import random

from gallery import GALLERY


EMOJI_LIST = ["💝", "💛", "💯", "🎁", "🎈", "🎉", "🎊", "💐", "🌹", "🌺", "🥳", "🤪", "🤗"]


class Holiday:
    """Holiday class instance"""

    def _construct_emoji_title(self):
        self.emoji_title = (
            self.title
            + f"{'!' * random.randint(3, 6)} {''.join(random.sample(EMOJI_LIST, random.randint(5, 8), counts=[3]*len(EMOJI_LIST)))}"
        )

    def __init__(self, title: str, image_path: str) -> None:
        self.title = title
        self.image_path = image_path
        self.image = GALLERY.read_image(self.image_path)
        self._construct_emoji_title()

    def as_tuple(self) -> tuple[str, str]:
        """Represents the Holiday class instance as tuple (str, str)

        Returns:
            tuple[str, str]
        """
        return (self.title, self.image_path)
