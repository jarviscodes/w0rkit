from colorama import Fore, Back, Style, init as colorama_init
from w0rkit.web.common.utils import format_dict_result
from flask import request, send_from_directory
from flask import Flask, Response
from ipaddress import IPv4Address
from pathlib import Path
import logging
import click


class EndpointAction(object):
    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args, **kwargs):
        new_response = self.action(**kwargs)
        if new_response:
            self.response = new_response
        return self.response


class FlaskAppWrapper(object):
    app = None

    def __init__(self, name, host, port):
        self.app = Flask(name)
        self.port = port

        # Make sure host and port are valid
        _ = IPv4Address(host)  # Throws exception on Invalid IPv4
        self.host = host

        if 1 < int(port) < 65535:
            self.port = port
        else:
            raise Exception(f"Port {port} is not a valid port to listen on!")

        # Disable logging for werkzeug
        logger = logging.getLogger("werkzeug")
        logger.setLevel(logging.ERROR)

    def run(self):
        self.app.run(host=self.host, port=self.port)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))


class WebMode(object):
    tool = "Web"
    last_query_params = None
    last_remote_address = None
    last_request_headers = None
    last_request_method = None

    def __init__(
        self,
        colorized=True,
        stager=True,
        stager_dir="/tmp/stager/",
        listen_host="0.0.0.0",
        listen_port=8000,
    ):
        self.colorized = colorized
        self.stager = stager
        self.stager_dir = stager_dir
        self.request_count = 0

        # Initialize the app and colorama
        colorama_init(autoreset=True)
        self.app_wrapper = FlaskAppWrapper(
            "webmode", host=listen_host, port=listen_port
        )
        self.app_wrapper.add_endpoint(
            endpoint="/", endpoint_name="web_mode", handler=self.action_handler
        )
        if stager:
            stager_path = Path(self.stager_dir)
            if not stager_path.exists():
                click.secho(
                    f"{Fore.LIGHTRED_EX}You specified stager path '{stager_path.absolute()}' but it does not exist on the filesystem."
                )
                exit()
            self.app_wrapper.add_endpoint(
                endpoint="/stager/<path:path>",
                endpoint_name="stager",
                handler=self.static_stager,
            )

    def action_handler(self):
        # Prepare print function to the user's preference
        printer = self.get_printer()

        # Store interesting stuff
        self.last_query_params = request.args
        self.last_remote_address = request.remote_addr
        self.last_request_headers = request.headers
        self.last_request_method = request.method

        # Output the incoming request
        printer(self.request_string)

        # Increment the request ID
        self.request_count += 1

        if self.last_header_count > 0:
            printer(self.header_string)

        if self.last_param_count > 0:
            printer(self.param_string)

    def get_printer(self):
        if self.colorized:
            return click.secho
        else:
            return click.echo

    def static_stager(self, path):
        remote_addr = request.remote_addr
        click.secho(
            f"[{self.tool}][Stager] {Fore.LIGHTCYAN_EX}Serving File: {Fore.YELLOW}{path} {Fore.LIGHTCYAN_EX}to {Fore.WHITE}{remote_addr}{Style.RESET_ALL}"
        )
        return send_from_directory(self.stager_dir, path)

    def run(self):
        self.app_wrapper.run()

    @property
    def header_string(self):
        hdr_count = self.last_header_count
        header_string = f"{Fore.WHITE}## {Fore.LIGHTCYAN_EX}Request Headers ({Fore.YELLOW}Count: {hdr_count}{Fore.LIGHTCYAN_EX}) {Fore.WHITE}##{Style.RESET_ALL}\n"
        header_string += len(header_string) * "-" + "\n"
        header_string += format_dict_result(self.last_request_headers)
        return header_string

    @property
    def param_string(self):
        param_count = self.last_param_count
        param_string = f"{Fore.WHITE}## {Fore.LIGHTCYAN_EX}Request Parameters ({Fore.YELLOW}Count: {param_count}{Fore.LIGHTCYAN_EX}) {Fore.WHITE}##{Style.RESET_ALL}\n"
        param_string += len(param_string) * "-" + "\n"
        param_string += format_dict_result(self.last_query_params)
        return param_string

    @property
    def request_string(self):
        return f"[{Fore.WHITE}ReqId: {Fore.GREEN}{self.request_count}{Style.RESET_ALL}][{Fore.LIGHTYELLOW_EX}{self.tool}{Style.RESET_ALL}]({Fore.LIGHTGREEN_EX}{self.mode}{Style.RESET_ALL}) {Fore.WHITE}{self.last_request_method} {Fore.LIGHTCYAN_EX}request from: {Fore.WHITE}{self.last_remote_address}{Style.RESET_ALL}"

    @property
    def last_header_count(self):
        return len(self.last_request_headers)

    @property
    def last_param_count(self):
        return len(self.last_query_params)
