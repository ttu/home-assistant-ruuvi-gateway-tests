# Ruuvi Gateway  Fetch Data Script

## Setup


Set IP, username and password to `fetch_data.py` script
```py
STATION_IP = "10.0.0.21"
USERNAME = "username"
PASSWORD = "password"
```
Create virtual env, install requirements and execute script
```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python fetch_data.py
```

## Get data

```
GET http://{ip}/history?time={time}
```

## Authentication

[auth.html](./gateway-fetch-script/auth.html) contains Gateway's login site's source code.

```
POST http://{ip}/auth

login: "xxxx"
password: "3449b7f88ae96091221a5b339fdb25b182a5f26ff6a068f92b076f9db2d36237"
```

* If request has WWW-Authenticate
  * Get challenge and real from header
  * MD5 for password
  * SHA256 for encrypted_password
  * POST auth {"login": user, "password": password_sha256 }
  * Redirect to Ruuvi-prev-url

```py
user = ""
password = ""

auth_str = request.getResponseHeader('WWW-Authenticate')

realm = _parseToken(auth_str, 'realm="', '"');
challenge = _parseToken(auth_str, 'challenge="', '"');

encrypted_password = CryptoJS.MD5(user + ':' + realm + ':' + password).toString();
password_sha256 = CryptoJS.SHA256(challenge + ':' + encrypted_password).toString();

# after auth
next_url = request.getResponseHeader('Ruuvi-prev-url')
```