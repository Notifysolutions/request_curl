# Request Curl

User-friendly wrapper for pycurl

## Installation
Use the package manager 
[pip](https://pip.pypa.io/en/stable/) 
to install request_curl.

```
pip install request_curl
```

## HTTP2
HTTP2 is disabled by default.

```python
import request_curl
s = request_curl.Session(http2=True)
r = s.get("https://www.example.com")
```

## Proxy Support
Proxy has to be formatted as a string.

```python
import request_curl
s = request_curl.Session()
r = s.get("https://www.example.com", proxies="ip:port:user:password")
```

## Content Decoding
```python
import request_curl
s = request_curl.Session(accept_encoding="br, gzip, deflate")
r = s.get("https://www.example.com", debug=True)
```

## Response Object

The response object behaves 
similar to the one of the requests library.

```python
import request_curl
s = request_curl.Session()
r = s.get("https://www.example.com")

print(r)
print(r.status_code)
print(r.content)
print(r.text)
print(r.json)
print(r.url)
print(r.history)
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
r = s.get("https://www.example.com")
```

## Debug Request
If debug is set to True the raw input 
and output headers will bre printed out.

```python
import request_curl
s = request_curl.Session()
r = s.get("https://www.example.com", debug=True)
```

## Custom Header
You can specify custom a customer header 
as a dictionary.

```python
import request_curl
s = request_curl.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
}
r = s.get("https://www.example.com", headers=headers)
```

## Install with Curl-Impersonate
- https://github.com/lwthiker/curl-impersonate/blob/main/INSTALL.md
- sudo apt install build-essential pkg-config cmake ninja-build curl autoconf automake libtool
- ``sudo apt install -y libbrotli-dev golang build-essential libnghttp2-dev cmake libunwind-dev libssl-dev git python3-dev``
- git clone https://github.com/pycurl/pycurl.git
- sudo python3 setup.py install --curl-config=/usr/local/bin/curl-impersonate-chrome-config

```python
import pycurl
pycurl.version_info()
# (9, '7.84.0', 480256, 'x86_64-pc-linux-gnu', 1370063517, 'BoringSSL', 0, '1.2.11', ('dict', 'file', 'ftp', 'ftps', 'gopher', 'gophers', 'http', 'https', 'imap', 'imaps', 'mqtt', 'pop3', 'pop3s', 'rtsp', 'smb', 'smbs', 'smtp', 'smtps', 'telnet', 'tftp'), None, 0, None)
quit()
```