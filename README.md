# w0rkit

A small toolkit containing response handling and parsing solutions that come in handy during PT/BH.

Disclaimer: Pls no evil :(

## Installation

1. `git clone ...`

2. `poetry install`

Done :-)

## Usage

Currently supports 2 modes. (`simple` and `b64d`).

### Simple
Just logs request source, headers and parameters. GET only.

`w0rkit simple -l [listen_address] -p [listen_port]`

### b64d
Fetches a `magic_param` from the GET query parameters, base64decodes it and removes url encoding.

`w0rkit b64d -l [listen_address] -p [listen_port] -m [magic_param]`

`-m` is optional and will default to `?q=`

**Note**: Setting `app(host=0.0.0.0)` seemed to default to default gw rather than actually 0.0.0.0.
Sucks when behind a vpn, so `-l` is obligatory in all instances, `-p` defaults to 5000.
