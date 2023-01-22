from http.cookiejar import CookieJar, Cookie
from io import BytesIO
from typing import Dict, Optional, List, Any, Union
import json as _json
from urllib.parse import quote_plus

import pycurl
from requests.cookies import cookiejar_from_dict, merge_cookies

from request_curl.helper import get_cookie
from request_curl.models import Response

DEFAULT_UA: str = "".join([
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1)"
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
])

DEFAULT_HEADER: Dict[str, str] = {
    "sec-ch-ua": ' Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": DEFAULT_UA,
    "Accept": "".join([
        "text/html,application/xhtml+xml,application/xml;q=0.9,",
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.9"
    ]),
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}

DEFAULT_CIPHER_SUITE: List[str] = [
    "TLS_AES_128_GCM_SHA256",
    "TLS_AES_256_GCM_SHA384",
    "TLS_CHACHA20_POLY1305_SHA256",
    "ECDHE-ECDSA-AES128-GCM-SHA256",
    "ECDHE-RSA-AES128-GCM-SHA256",
    "ECDHE-ECDSA-AES256-GCM-SHA384",
    "ECDHE-RSA-AES256-GCM-SHA384",
    "ECDHE-ECDSA-CHACHA20-POLY1305",
    "ECDHE-RSA-CHACHA20-POLY1305",
    "ECDHE-RSA-AES128-SHA",
    "ECDHE-RSA-AES256-SHA",
    "AES128-GCM-SHA256",
    "AES256-GCM-SHA384",
    "AES128-SHA",
    "AES256-SHA",
]


class Session:
    """A request_curl session.
    Provides cookie persistence, connection-pooling, and configuration.

    Basic Usage::

      >>> import request_curl
      >>> s = request_curl.Session()
      >>> s.get('https://httpbin.org/get')
      <Response [200]>

    Or as a context manager::

      >>> with request_curl.Session() as session:
      ...     s.get('https://httpbin.org/get')
      <Response [200]>
    """
    def __init__(
        self,
        headers: Dict[str, str] = DEFAULT_HEADER,
        cipher_suite: List[str] = DEFAULT_CIPHER_SUITE,
        proxies: str = "",
        http2: bool = False,
        accept_encoding: str = "gzip, deflate"
    ):
        self._curl = pycurl.Curl()
        self._curl.setopt(pycurl.ACCEPT_ENCODING, accept_encoding)

        if http2:
            self._curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2_0)
        else:
            self._curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)

        if proxies:
            self.__set_proxies(proxies)
        else:
            self._curl.setopt(pycurl.PROXY, "")
            self._curl.setopt(pycurl.PROXYUSERPWD, "")

        self._curl.setopt(pycurl.SSL_CIPHER_LIST, ",".join(cipher_suite))

        if not headers.get("user-agent"):
            headers['user-agent'] = DEFAULT_UA

        if headers:
            self._curl.setopt(
                pycurl.HTTPHEADER,
                [f"{k}: {v}" for k, v in headers.items()]
            )
        else:
            self._curl.setopt(
                pycurl.HTTPHEADER,
                [f"{k}: {v}" for k, v in DEFAULT_HEADER.items()]
            )

        self.cookies: CookieJar = cookiejar_from_dict({})

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._curl.close()

    def __set_proxies(self, proxies: str) -> None:
        proxy_split: List[str] = proxies.split(":")
        self._curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
        self._curl.setopt(pycurl.PROXY, f"{proxy_split[0]}:{proxy_split[1]}")
        if len(proxy_split) > 3:
            self._curl.setopt(pycurl.PROXYUSERPWD, f"{proxy_split[2]}:{proxy_split[3]}")

    def __add_cookies_to_session(self, cookies: CookieJar) -> None:
        self.cookies = merge_cookies(self.cookies, cookies)

    def add_cookie(self, name: str, value: str, domain: str = "") -> None:
        self.cookies.set_cookie(get_cookie(name, value, domain))

    def remove_all_cookies(self) -> None:
        self.cookies = cookiejar_from_dict({})

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = DEFAULT_HEADER,
        proxies: Optional[str] = None,
        timeout: Union[float, int] = 60,
        allow_redirects: bool = True,
        http2: bool = True,
        verify: bool = True
    ):
        """Constructs a :class:`Request <Request>`, prepares it and sends it.
        Returns :class:`Response <Response>` object.

        :param method: method for the new :class:`Request` object.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query
            string for the :class:`Request`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the
            :class:`Request`.
        :param headers: (optional) Dictionary of HTTP Headers to send with the
            :class:`Request`.
        :param proxies: (optional) URL of the proxy.
        :type proxies: string
        :param timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param allow_redirects: (optional) Set to True by default.
        :type allow_redirects: bool
        :param http2: (optional) Set http2 to True by default.
        :type http2: bool
        :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``. When set to
            ``False``, requests will accept any TLS certificate presented by
            the server, and will ignore hostname mismatches and/or expired
            certificates, which will make your application vulnerable to
            man-in-the-middle (MitM) attacks. Setting verify to ``False``
            may be useful during local development or testing.
        :rtype: requests.Response
        """

        if method.upper() == "POST":
            self._curl.setopt(pycurl.POST, 1)
        elif method.upper() == "GET":
            self._curl.setopt(pycurl.HTTPGET, 1)
        elif method.upper() == "HEAD":
            self._curl.setopt(pycurl.NOBODY, 1)
        else:
            self._curl.setopt(pycurl.CUSTOMREQUEST, method.upper())

        if params:
            url = url + "?" + "&".join([f"{k}={v};" for k, v in params.items()])

        self._curl.setopt(pycurl.URL, url)

        if not verify:
            self._curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            self._curl.setopt(pycurl.SSL_VERIFYHOST, 0)

        if proxies:
            self.__set_proxies(proxies)

        if not http2:
            self._curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)

        self._curl.setopt(pycurl.FOLLOWLOCATION, allow_redirects)
        self._curl.setopt(pycurl.TIMEOUT, timeout)

        if data:
            form: List[str] = [f"{k}={v}" for k, v in data.items()]
            self._curl.setopt(pycurl.POSTFIELDS, "&".join(form).encode("utf-8"))

        if json:
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            headers["charset"] = "utf-8"
            if isinstance(json, dict):
                json_data = _json.dumps(json)
                self._curl.setopt(pycurl.POSTFIELDS, json_data)

        if self.cookies:
            chunks = []
            for cookie in self.cookies:
                name, value = quote_plus(cookie.name), quote_plus(cookie.value)
                chunks.append(f"{name}={value};")
            if chunks:
                self._curl.setopt(pycurl.COOKIE, "".join(chunks))
        else:
            self._curl.setopt(pycurl.COOKIELIST, "")

        body_output: BytesIO = BytesIO()
        headers_output: BytesIO = BytesIO()
        self._curl.setopt(pycurl.HEADERFUNCTION, headers_output.write)
        self._curl.setopt(pycurl.WRITEFUNCTION, body_output.write)

        self._curl.perform()

        response = Response(self._curl, body_output, headers_output)
        self.__add_cookies_to_session(response.cookies)

        return response

    def debug_function(self, t, b):
        if t in [1, 2, 5, 6]:
            self.debug_entries.append(b.decode("utf-8"))

    def get(self, url, **kwargs):
        r"""Sends a GET request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        r"""Sends a POST request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """

        return self.request('POST', url, **kwargs)

    def options(self, url, **kwargs):
        return self.request('OPTIONS', url, **kwargs)
