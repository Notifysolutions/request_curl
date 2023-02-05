import re
from io import BytesIO
import json
from typing import List, Optional, Dict, Any
import zlib
from http.cookiejar import CookieJar

import brotli
import pycurl

from request_curl.dict import CaseInsensitiveDict
from request_curl.helper import to_cookiejar

CURL_INFO_MAPPING: Dict[str, Any] = {
    "TOTAL_TIME": pycurl.TOTAL_TIME,
    "NAMELOOKUP_TIME": pycurl.NAMELOOKUP_TIME,
    "CONNECT_TIME": pycurl.CONNECT_TIME,
    "APPCONNECT_TIME": pycurl.APPCONNECT_TIME,
    "PRETRANSFER_TIME": pycurl.PRETRANSFER_TIME,
    "STARTTRANSFER_TIME": pycurl.STARTTRANSFER_TIME,
    "REDIRECT_TIME": pycurl.REDIRECT_TIME,
    "HTTP_CODE": pycurl.HTTP_CODE,
    "REDIRECT_COUNT": pycurl.REDIRECT_COUNT,
    "REDIRECT_URL": pycurl.REDIRECT_URL,
    "SIZE_UPLOAD": pycurl.SIZE_UPLOAD,
    "SIZE_DOWNLOAD": pycurl.SIZE_DOWNLOAD,
    "SPEED_DOWNLOAD": pycurl.SPEED_DOWNLOAD,
    "SPEED_UPLOAD": pycurl.SPEED_UPLOAD,
    "HEADER_SIZE": pycurl.HEADER_SIZE,
    "REQUEST_SIZE": pycurl.REQUEST_SIZE,
    "SSL_VERIFYRESULT": pycurl.SSL_VERIFYRESULT,
    "SSL_ENGINES": pycurl.SSL_ENGINES,
    "CONTENT_LENGTH_DOWNLOAD": pycurl.CONTENT_LENGTH_DOWNLOAD,
    "CONTENT_LENGTH_UPLOAD": pycurl.CONTENT_LENGTH_UPLOAD,
    "CONTENT_TYPE": pycurl.CONTENT_TYPE,
    "HTTPAUTH_AVAIL": pycurl.HTTPAUTH_AVAIL,
    "PROXYAUTH_AVAIL": pycurl.PROXYAUTH_AVAIL,
    "OS_ERRNO": pycurl.OS_ERRNO,
    "NUM_CONNECTS": pycurl.NUM_CONNECTS,
    "PRIMARY_IP": pycurl.PRIMARY_IP,
    "CURLINFO_LASTSOCKET": pycurl.LASTSOCKET,
    "EFFECTIVE_URL": pycurl.EFFECTIVE_URL,
    "INFO_COOKIELIST": pycurl.INFO_COOKIELIST,
    "RESPONSE_CODE": pycurl.RESPONSE_CODE,
    "HTTP_CONNECTCODE": pycurl.HTTP_CONNECTCODE,
}

HTTP_RES_HDR = re.compile(r"(?P<version>HTTP\/.*?)\s+(?P<code>\d{3})\s+(?P<message>.*)")


class Response:
    def __init__(
        self, curl: pycurl.Curl, body_output: BytesIO, headers_output: BytesIO
    ):
        self._curl: pycurl.Curl = curl

        self._body_output: BytesIO = body_output
        self._headers_output: BytesIO = headers_output

        self._status_code: Optional[int] = int(self._curl.getinfo(pycurl.HTTP_CODE))
        self._time_info = None
        self._content = False
        self._url = None
        self._text = None
        self._headers = None
        self._history: List[Any] = []
        self._headers_history: List[Any] = []
        self._cookie_jar = None

        self._response_info = {}
        self.__get_curl_info()
        self.__parse_headers_raw()
        self.__set_text()

    @property
    def url(self):
        return self._url

    @property
    def status_code(self):
        return self._status_code

    @property
    def headers(self):
        return self._headers

    @property
    def json(self) -> Optional[dict]:
        try:
            return json.loads(self._text)
        except ValueError:
            return None

    @property
    def content(self) -> Optional[bytes]:
        try:
            return self._body_output.getvalue()
        except ValueError:
            return None

    @property
    def text(self) -> str:
        return self._text

    def __set_text(self):
        try:
            if not self._text:
                if "gzip" in self.__get_header_value("Content-Encoding"):
                    try:
                        if "ISO-8859-1" in self.__get_header_value("Content-Type"):
                            self._text = self.__decode_gzip(self._body_output).decode(
                                "ISO-8859-1", errors="ignore"
                            )
                        else:
                            self._text = self.__decode_gzip(self._body_output).decode(
                                "UTF-8", errors="ignore"
                            )

                    except zlib.error:
                        pass
                elif "br" in self.__get_header_value("Content-Encoding"):
                    try:
                        self._text = self.__decode_br(self._body_output).decode(
                            "UTF-8", errors="ignore"
                        )
                    except Exception as e:
                        pass
                else:
                    self._text = self._body_output.getvalue().decode(
                        "UTF-8", errors="ignore"
                    )
        except Exception:
            self._text = None

    @property
    def cookies(self) -> CookieJar:
        if not self._cookie_jar:
            self._cookie_jar = to_cookiejar(self._curl.getinfo(4194332), self.headers)
        return self._cookie_jar

    def __parse_headers_raw(self):
        def parse_header_block(header_raw_block: List[str]):
            block_headers = []
            for header in header_raw_block:
                if not header.startswith("HTTP"):
                    key, value = map(lambda u: u.strip(), header.split(":", 1))
                    block_headers.append((key, value))

            return block_headers

        raw_headers = self._headers_output.getvalue().decode("UTF-8")

        self._headers = CaseInsensitiveDict(
            parse_header_block(self.__split_headers_blocks(raw_headers)[-1])
        )

    @staticmethod
    def __split_headers_blocks(raw_headers):
        i = 0
        blocks = []
        for item in raw_headers.strip().split("\r\n"):
            if item.startswith("HTTP"):
                blocks.append([item])
                i = len(blocks) - 1
            elif item:
                blocks[i].append(item)
        return blocks

    @staticmethod
    def __decode_gzip(content):
        return zlib.decompress(content.getvalue(), zlib.MAX_WBITS | 16)

    @staticmethod
    def __decode_br(content):
        return brotli.decompress(content.getvalue())

    def __get_curl_info(self) -> dict:
        for key, value in CURL_INFO_MAPPING.items():
            try:
                key_data = self._curl.getinfo(value)
            except Exception as e:
                continue
            else:
                self._response_info[key] = key_data
        self._url = self._response_info.get("EFFECTIVE_URL")
        return self._response_info

    def __get_header_value(self, key: str) -> str:
        for k, value in self.headers.items():
            if k.lower() == key.lower():
                return value

        return ""
