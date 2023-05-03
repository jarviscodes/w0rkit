import click
from colorama import Fore, Back, Style, init as colorama_init
from flask import g


VERSION = "0.0.1"

colorama_init(autoreset=True)


@click.group()
def main():
    print(f"W0rkit CLI {VERSION}")


@main.command()
@click.option("-l", "--listen_address", help="Address the server should listen on.", required=True)
@click.option("-p", "--listen_port", help="Port to listen on.", required=True)
def simple(listen_address, listen_port):
    from w0rkit.web.simple_mode import app
    showmode("Simple", listen_address, listen_port)
    app.run(host=listen_address, port=listen_port)


@main.command()
@click.option("-l", "--listen_address", help="Address the server should listen on.", required=True)
@click.option("-p", "--listen_port", help="Port to listen on.", required=True)
@click.option("-m", "--magic_param", help="The GET parameter containing your base64 data.")
def b64d(listen_address, listen_port, magic_param):
    from w0rkit.web.simple_b64 import app
    showmode("B64Decoder <3", listen_address, listen_port, magic_param=magic_param)

    if not magic_param:
        click.secho(f"{Fore.LIGHTYELLOW_EX}No magic param specified (-m)! Defaulting to '?q='{Style.RESET_ALL}")
        magic_param = "q"
    app.config['MAGIC_PARAM'] = magic_param
    app.run(host=listen_address, port=listen_port)


def showmode(mode, host, port, **kwargs):
    click.secho(f"{Fore.LIGHTYELLOW_EX}{mode} {Fore.LIGHTCYAN_EX}mode. Running on {Fore.WHITE}{host}:{port}{Style.RESET_ALL}")

    # Magic param set?
    magic_param = kwargs.get('magic_param', None)
    if magic_param:
        click.secho(f"{Fore.LIGHTCYAN_EX}Checking parameter: {Fore.WHITE}{magic_param}")