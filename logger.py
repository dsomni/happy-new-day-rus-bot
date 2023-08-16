"""Contains the Logger class instances"""

from typing import Any, Iterable, Literal, Union

from tqdm import tqdm
from settings import SETTINGS_MANAGER

MessageType = Union[Literal["Info"], Literal["Warning"], Literal["Error"]]


class Logger:
    """Manages console logs"""

    def log(self, message: str, message_type: MessageType = "Info") -> None:
        """Logs message to console if needed

        Args:
            message (str): message to print
            message_type (MessageType, optional): type of message. Defaults to "Info".
        """

        if message_type == "Error" or SETTINGS_MANAGER.should_log():
            print(message)

    def get_tqdm(self, sequence: Iterable, *args: Any, **kwargs: Any) -> Iterable:
        """Wraps the iterable in tqdm if needed

        Args:
            sequence (Iterable): iterable sequence

        Returns:
            Iterable: sequence
        """

        if SETTINGS_MANAGER.should_log():
            return tqdm(sequence, *args, **kwargs)
        return sequence


LOGGER = Logger()
