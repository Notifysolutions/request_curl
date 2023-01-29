from http.cookiejar import CookieJar, Cookie
from typing import Tuple, List, Union, Dict
from http.cookies import SimpleCookie


def to_cookiejar(cookies: Union[str, CookieJar], headers: Dict[str, str]) -> CookieJar:
    if isinstance(cookies, CookieJar):
        return cookies

    _cookies: List[Tuple[str, str, str]] = [
        (get_cookie_name(cookie), get_cookie_value(cookie), "") for cookie in cookies
    ]

    cookie_jar: CookieJar = CookieJar()

    for name, value, domain in _cookies:
        cookie_jar.set_cookie(get_cookie(name, value, domain))

    for key, value in headers.items():
        if key.lower() != "set-cookie":
            continue

        header_set_cookie = SimpleCookie()
        header_set_cookie.load(value)

        for n, v in header_set_cookie.items():
            cookie_jar.set_cookie(get_cookie(n, v.value, ""))

    return cookie_jar


def get_cookie(name: str, value: str, domain: str):
    return Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain=domain,
        domain_specified=False,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=False,
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={"HttpOnly": ""},
        rfc2109=False,
    )


def get_cookie_name(cookie: str) -> str:
    try:
        return cookie.split("\t")[-2]
    except IndexError:
        return ""


def get_cookie_value(cookie: str) -> str:
    try:
        return cookie.split("\t")[-1]
    except IndexError:
        return ""


def get_cookie_domain(cookie: str) -> str:
    try:
        return cookie.split("\t")[0]
    except IndexError:
        return ""
