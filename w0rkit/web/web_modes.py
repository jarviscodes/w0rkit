import binascii
from base64 import b64decode
from urllib.parse import unquote
from w0rkit.web.web_core import WebMode
from colorama import Fore, Style


class SimpleMode(WebMode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = "Simple"


class Base64Mode(WebMode):
    def __init__(self, magic_param, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = "B64Decoder"
        self.magic_param = magic_param
        printer = self.get_printer()
        if not self.magic_param:
            printer(
                f"{Fore.LIGHTYELLOW_EX}No magic param specified (-m)! Defaulting to '?q='{Style.RESET_ALL}"
            )
            self.magic_param = "q"

    def action_handler(self):
        decode_failed = False
        printer = self.get_printer()
        # First call base handler for header info and setting members.
        super().action_handler()

        # Get our magic param from the request
        magic_value = self.last_query_params.get(self.magic_param)
        # Prepare the buffer as empty
        magic_value_unquoted = ""
        if magic_value and len(magic_value) != 0:
            # Prepare b64 payload
            try:
                magic_value_decoded = b64decode(magic_value).decode("utf-8")
                magic_value_unquoted = unquote(magic_value_decoded)
            except binascii.Error:
                decode_failed = True

        if not decode_failed:
            if len(magic_value_unquoted) > 0:
                printer(
                    "-----------------------------------------------------------------------------------------------------"
                )
                printer(
                    f"{Fore.WHITE}## {Fore.LIGHTCYAN_EX}Decoded Data {Fore.WHITE}##{Style.RESET_ALL}\n{magic_value_unquoted}"
                )
            else:
                printer("No magic value in this request, not decoding anything.")
        else:
            printer(
                "We did find a magic value, but we did not manage to decode it. (Likely not base64 or invalid padding)"
            )
