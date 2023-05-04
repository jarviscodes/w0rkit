from flask import request, send_from_directory
import click
from colorama import Fore, Back, Style

def stager_route(path):
    remote_addr = request.remote_addr
    click.secho(f"[Stager] {Fore.LIGHTCYAN_EX}Serving File: {Fore.YELLOW}{path} {Fore.LIGHTCYAN_EX}to {Fore.WHITE}{remote_addr}{Style.RESET_ALL}")
    return send_from_directory('static/payloads/', path)