from http.cookiejar import CookieJar
from io import BytesIO
from typing import Dict, Optional, List, Any, Union
import json as _json
from urllib.parse import quote_plus

import pycurl
from requests.cookies import cookiejar_from_dict, merge_cookies

from request_curl.helper import get_cookie
from request_curl.models import Response


class Session:
    """A request_curl session.
    Provides cookie persistence, connection-pooling, and configuration.

    Basic Usage::

      >>> import request_curl
      >>> s = request_curl.Session()
      >>> s.get('https://httpbin.org/get')
      <Response [200]>

    Or as a context manager::

      >>> with request_curl.Session() as s:
      ...     s.get('https://httpbin.org/get')
      <Response [200]>
    """

    def __init__(
        self,
        headers: Dict[str, str] = None,
        cipher_suite: List[str] = None,
        http2: bool = False,
        proxies: str = "",
    ):
        self.curl = pycurl.Curl()
        self.headers = headers if headers else {}
        self.cipher_suite = cipher_suite if cipher_suite else []
        self.http2 = http2
        self.proxies = proxies

        self.__debug_entries = []
        self.cookies = cookiejar_from_dict({})

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.curl.close()

    def __set_settings(self):
        if self.headers:
            self.curl.setopt(
                pycurl.HTTPHEADER, [f"{k}: {v}" for k, v in self.headers.items()]
            )

        if self.http2:
            self.curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2_0)
        else:
            self.curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)

        if len(self.proxies) > 0:
            self.__set_proxies()

        if len(self.cipher_suite) > 0:
            self.curl.setopt(pycurl.SSL_CIPHER_LIST, ",".join(self.cipher_suite))

    def __set_proxies(self) -> None:
        proxy_split: List[str] = self.proxies.split(":")
        self.curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
        self.curl.setopt(pycurl.PROXY, f"{proxy_split[0]}:{proxy_split[1]}")
        if len(proxy_split) > 3:
            self.curl.setopt(pycurl.PROXYUSERPWD, f"{proxy_split[2]}:{proxy_split[3]}")

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
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        proxies: Optional[str] = None,
        timeout: Union[float, int] = 60,
        allow_redirects: bool = True,
        http2: bool = False,
        verify: bool = True,
        debug: bool = False,
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
        :type timeout: float
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
        :param debug: (optional) Set debug mode.
        :type debug: bool
        :rtype: Response
        """
        self.curl.reset()
        self.__set_settings()

        if method.upper() == "POST":
            self.curl.setopt(pycurl.POST, 1)
        elif method.upper() == "GET":
            self.curl.setopt(pycurl.HTTPGET, 1)
        elif method.upper() == "HEAD":
            self.curl.setopt(pycurl.NOBODY, 1)
        else:
            self.curl.setopt(pycurl.CUSTOMREQUEST, method.upper())

        if params:
            url = url + "?" + "&".join([f"{k}={v};" for k, v in params.items()])

        self.curl.setopt(pycurl.URL, url)
        self.curl.setopt(pycurl.FOLLOWLOCATION, allow_redirects)
        self.curl.setopt(pycurl.TIMEOUT, timeout)

        if not verify:
            self.curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            self.curl.setopt(pycurl.SSL_VERIFYHOST, 0)

        if proxies:
            self.proxies = proxies
            self.__set_proxies()

        if http2:
            self.curl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2_0)

        if headers:
            self.curl.setopt(
                pycurl.HTTPHEADER, [f"{k}: {v}" for k, v in headers.items()]
            )

        if data:
            form: List[str] = [f"{k}={v}" for k, v in data.items()]
            self.curl.setopt(pycurl.POSTFIELDS, "&".join(form).encode("utf-8"))

        if json:
            headers = headers.copy() if headers else self.headers.copy()
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
            headers["charset"] = "utf-8"

            self.curl.setopt(
                pycurl.HTTPHEADER, [f"{k}: {v}" for k, v in headers.items()]
            )

            if isinstance(json, dict):
                json_data = _json.dumps(json)
                self.curl.setopt(pycurl.POSTFIELDS, json_data)

        if self.cookies:
            chunks = []
            for cookie in self.cookies:
                name, value = quote_plus(cookie.name), quote_plus(cookie.value)
                chunks.append(f"{name}={value};")
            if chunks:
                self.curl.setopt(pycurl.COOKIE, "".join(chunks))

        if debug:
            self.__debug_entries = []
            self.curl.setopt(pycurl.VERBOSE, 1)

        body_output: BytesIO = BytesIO()
        headers_output: BytesIO = BytesIO()
        self.curl.setopt(pycurl.HEADERFUNCTION, headers_output.write)
        self.curl.setopt(pycurl.WRITEFUNCTION, body_output.write)

        self.curl.perform()

        if debug:
            print("\n".join(self.__debug_entries))

        response = Response(self.curl, body_output, headers_output)
        self.__add_cookies_to_session(response.cookies)

        return response

    def debug_function(self, t, b):
        if t in [1, 2, 5, 6]:
            self.__debug_entries.append(b.decode("utf-8"))

    def get(self, url, **kwargs):
        r"""Sends a GET request. Returns :class:`Response` object."""
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        r"""Sends a POST request. Returns :class:`Response` object."""
        return self.request("POST", url, **kwargs)

    def options(self, url, **kwargs):
        r"""Sends a OPTIONS request. Returns :class:`Response` object."""
        return self.request("OPTIONS", url, **kwargs)

    def delete(self, url, **kwargs):
        r"""Sends a DELETE request. Returns :class:`Response` object."""
        return self.request("DELETE", url, **kwargs)

    def put(self, url, **kwargs):
        r"""Sends a PUT request. Returns :class:`Response` object."""
        return self.request("PUT", url, **kwargs)
