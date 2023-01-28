# Request Curl

User-friendly wrapper for pycurl

## Installation
Use the package manager 
[pip](https://pip.pypa.io/en/stable/) 
to install request_curl.

```
pip install request_curl
```

# Quickstart
A request_curl session provides cookie persistence, connection-pooling, and configuration.

Basic Usage:
```python
import request_curl
s = request_curl.Session()
s.get('https://httpbin.org/get')
# <Response [200]>
```

Or as a context manager:
```python
import request_curl
with request_curl.Session() as session:
    session.get('https://httpbin.org/get')
# <Response [200]>
```

## Response Object

The response object behaves
similar to the one of the [requests](https://pypi.org/project/requests/)' library.

```python
import request_curl
s = request_curl.Session()
r = s.get("https://httpbin.org/get")

print(r)
print(r.status_code)
print(r.content)
print(r.text)
print(r.json)
print(r.url)
```

## Proxy Support
Proxy has to be formatted as a string.

```python
import request_curl
s = request_curl.Session()
r = s.get("https://httpbin.org/get", proxies="ip:port:user:password")
# r = s.get("https://httpbin.org/get", proxies="ip:port")
```

## Content Decoding
```python
import request_curl
s = request_curl.Session(accept_encoding="br, gzip, deflate")
r = s.get("https://httpbin.org/get", debug=True)
```

## HTTP2
HTTP2 is disabled by default.

```python
import request_curl
s = request_curl.Session(http2=True)
r = s.get("https://httpbin.org/get")
```

## Cipher Suites
You can specify custom cipher suites as an array.

```python
import request_curl

cipher_suite = [
    "AES128-SHA256",
    "AES256-SHA256",
    "AES128-GCM-SHA256",
    "AES256-GCM-SHA384"
]
s = request_curl.Session(cipher_suite=cipher_suite)
r = s.get("https://httpbin.org/get")
```

## Debug Request
If debug is set to True the raw input 
and output headers will bre printed out.

```python
import request_curl
s = request_curl.Session()
r = s.get("https://httpbin.org/get", debug=True)
```

## Custom Headers
You can specify custom a customer header 
as a dictionary.

```python
import request_curl
s = request_curl.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
}
r = s.get("https://httpbin.org/get", headers=headers)
```

## License
Ennis Blank <Ennis.Blank@hotmail.com>, Mauritz Uphoff <Mauritz.Uphoff@me.com>

[MIT](LICENSE)