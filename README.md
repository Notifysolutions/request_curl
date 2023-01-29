# Request Curl

A user-friendly wrapper for pycurl that simplifies HTTP requests.

## Installation
Use the package manager 
[pip](https://pip.pypa.io/en/stable/) 
to install request_curl.

```
pip install request_curl
```

# Quickstart
A request_curl session manages cookies, connection pooling, and configurations.

Basic Usage:
```python
import request_curl
s = request_curl.Session()
s.get('https://httpbin.org/get') # returns <Response [200]>
s.request('GET', 'https://httpbin.org/get') # returns <Response [200]>
```

Using a Context Manager
```python
import request_curl
with request_curl.Session() as session:
    session.get('https://httpbin.org/get') # returns <Response [200]>
```

# Features

## Response Object

The response object is similar to that of the [requests](https://pypi.org/project/requests/) library.

```python
import request_curl
s = request_curl.Session()
r = s.get("https://httpbin.org/get")

print(r) # prints response object
print(r.status_code) # prints status code
print(r.content) # prints response content in bytes
print(r.text) # prints response content as text
print(r.json) # prints response content as JSON
print(r.url) # prints response URL
print(r.headers) # prints response URL
```

## Proxy Support
Format the proxy as a string.

```python
import request_curl
s = request_curl.Session()
# supports authentication: r = s.get("https://httpbin.org/get", proxies="ip:port:user:password")
r = s.get("https://httpbin.org/get", proxies="ip:port")
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
Set debug to True to print raw input and output headers.

```python
import request_curl
s = request_curl.Session()
r = s.get("https://httpbin.org/get", debug=True)
```

## Custom Headers
Specify custom headers as a dictionary.

```python
import request_curl
s = request_curl.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
}
r = s.get("https://httpbin.org/get", headers=headers)
```

## Data

```python
import request_curl
s = request_curl.Session()

# sending form data
form_data = {"key": "value"}
response = s.post("https://httpbin.org/post", data=form_data)

# sending json data
json_data = {"key": "value"}
response = s.post("https://httpbin.org/post", json=json_data)
```

# Contributing

We welcome contributions through pull requests. 
Before making major changes, please open an issue to discuss your intended changes.
Also, ensure to update relevant tests.

# License
Ennis Blank <Ennis.Blank@fau.de>, Mauritz Uphoff <Mauritz.Uphoff@hs-osnabrueck.de>

[MIT](LICENSE)