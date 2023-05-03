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

So with `-l 127.0.0.1` and `-p 80`:
```
$ curl "http://localhost/?query1=foo&query2=bar&something=somethingelse"
OK
```

Result:

![Result](img/simple.png)

### b64d
Fetches a `magic_param` from the GET query parameters, base64decodes it and removes url encoding.

`w0rkit b64d -l [listen_address] -p [listen_port] -m [magic_param]`
`-m` is optional and will default to `?q=`

So with `-l 127.0.0.1`, `-p 80` and `-m decodeme`:

```http
$ curl "http://localhost/?decodeme=JTNDaHRtbCUzRSUwQSUzQ2hlYWQlM0UlMEElM0N0aXRsZSUzRU9oJTIwd293JTJDJTIwc28lMjByZWFkYWJsZSUzQy90aXRsZSUzRSUwQSUzQy9oZWFkJTNFJTBBJTNDYm9keSUzRSUwQSUzQy9ib2R5JTNFJTBBJTNDL2h0bWwlM0U%3D%3D"
OK
```

Result:

![Result](img/b64d.png)


Happy Hunting!
