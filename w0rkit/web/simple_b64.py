import os.path

from flask import Flask, request, g, send_from_directory
import logging
import click
from colorama import Fore, Back, Style, init as colorama_init
from urllib.parse import unquote
from base64 import b64decode

# Initialize the app and colorama
app = Flask(__name__)
colorama_init(autoreset=True)

# Disable logging for werkzeug
logger = logging.getLogger("werkzeug")
logger.setLevel(logging.ERROR)


@app.get("/")
def home():
    # Prepare magic_param value
    test_parameter = app.config.get("MAGIC_PARAM")

    # Initialize some parameters
    query_parameters = request.args
    remote_address = request.remote_addr
    request_headers = request.headers
    request_method = request.method

    magic_value = query_parameters.get(test_parameter)
    # Prepare the buffer as empty
    magic_value_unquoted = ""
    if magic_value and len(magic_value) != 0:
        # Prepare b64 payload
        magic_value_decoded = b64decode(magic_value).decode("utf-8")
        magic_value_unquoted = unquote(magic_value_decoded)

    # Formatting goes brrr.
    remote_address_f = f"{Fore.WHITE}{request_method} {Fore.LIGHTCYAN_EX}request from: {Fore.WHITE}{remote_address}{Style.RESET_ALL}"

    hdr_count = len(request_headers)
    request_headers_f = ""
    for k in request_headers.keys():
        request_headers_f += (
            f"{Fore.LIGHTCYAN_EX}{k}: {Fore.WHITE}{request_headers[k]}{Style.RESET_ALL}\n"
        )

    param_count = len(query_parameters)
    query_params_f = f""
    for k in query_parameters.keys():
        query_params_f += f"{Fore.LIGHTCYAN_EX}{k}: {Fore.WHITE}{query_parameters[k]}{Style.RESET_ALL}\n"

    # Readability
    click.secho("=====================================================================================================")
    # Dump everything
    click.secho(remote_address_f)
    if hdr_count > 0:
        click.secho(
            "-----------------------------------------------------------------------------------------------------")
        click.secho(
            f"{Fore.WHITE}## {Fore.LIGHTCYAN_EX}Request Headers ({Fore.YELLOW}Count: {hdr_count}{Fore.LIGHTCYAN_EX}) {Fore.WHITE}##{Style.RESET_ALL}"
        )
        click.secho(request_headers_f)

    if param_count > 0:
        click.secho(
            "-----------------------------------------------------------------------------------------------------")
        click.secho(
            f"{Fore.WHITE}## {Fore.LIGHTCYAN_EX}Request Parameters ({Fore.YELLOW}Count: {param_count}{Fore.LIGHTCYAN_EX}) {Fore.WHITE}##{Style.RESET_ALL}"
        )
        click.secho(query_params_f)

    if len(magic_value_unquoted) > 0:
        click.secho(
            "-----------------------------------------------------------------------------------------------------")
        click.secho(
            f"{Fore.WHITE}## {Fore.LIGHTCYAN_EX}Decoded Data {Fore.WHITE}##{Style.RESET_ALL}\n{magic_value_unquoted}"
        )
    else:
        click.secho("No magic value in this request, not decoding anything.")

    # Return something to keep the client (and flask) happy, just in case.
    return "OK"


@app.get("/stager/<path:path>")
def send_payload(path):
    remote_addr = request.remote_addr
    click.secho(f"[Stager] {Fore.LIGHTCYAN_EX}Serving File: {Fore.YELLOW}{path} {Fore.LIGHTCYAN_EX}to {Fore.WHITE}{remote_addr}{Style.RESET_ALL}")
    return send_from_directory('static/payloads/', path)
