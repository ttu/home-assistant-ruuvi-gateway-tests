# home-assistant-ruuvi-gateway-tests

Test files and notes for Ruuvi Gateway scripts, packages and Home Assistant component.

Will be eventually moved under [Ruuvi Friends organization](https://github.com/ruuvi-friends).

## Home Assistant Component

TODO

## Ruuvi Gateway fetch data script

Released implementation in [ruuvi-friends/ruuvi-gateway-fetch-data-script](https://github.com/ruuvi-friends/ruuvi-gateway-fetch-data-script)

Local [README & Notes](/gateway-fetch-script/README.md)

## Gateway package

Ruuvi Gateway package test

https://packaging.python.org/en/latest/tutorials/packaging-projects/

Install

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ./ruuvi_gateway
```

Execute tests

```sh
python setup.py test
```


Test package

```sh
python example.py
```
