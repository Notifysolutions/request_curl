import request_curl
from request_curl import CHROME_CIPHER_SUITE, CHROME_HEADERS, CHROME_UA
from request_curl.dict import CaseInsensitiveDict

TLS_API: str = "https://tls.notifysolutions.eu/api/all"
HTTP_BIN_API: str = "https://httpbin.org"
BROWSER_LEAKS: str = "https://tls.browserleaks.com/json"
GOOGLE: str = "https://google.com"


def test_context_manager():
    with request_curl.Session() as session:
        r = session.get(HTTP_BIN_API + "/get")
        assert r.status_code == 200


def test_http_version(session):
    session.http2 = True
    response = session.get(TLS_API, verify=False).json
    assert response.get("http_version") == "h2"

    session.http2 = False
    response = session.get(TLS_API, verify=False).json
    assert response.get("http_version") == "HTTP/1.1"


def test_request_methods(session):
    assert session.get(TLS_API).json["method"] == "GET"
    assert session.post(TLS_API).json["method"] == "POST"
    assert session.options(TLS_API).json["method"] == "OPTIONS"
    assert session.delete(TLS_API).json["method"] == "DELETE"
    assert session.put(TLS_API).json["method"] == "PUT"


def test_response_object_props(session):
    for url in [TLS_API, HTTP_BIN_API + "/get"]:
        response = session.get(url)

        assert isinstance(response.status_code, int) and response.status_code >= 0
        assert isinstance(response.content, bytes) and len(response.content) > 0
        assert isinstance(response.text, str) and len(response.text) > 0
        assert isinstance(response.json, dict) and len(response.json) > 0
        assert isinstance(response.url, str) and len(response.url) > 0


def test_custom_cipher_suite(session):
    session.cipher_suite = [
        "AES128-SHA256",
        "AES256-SHA256",
        "AES128-GCM-SHA256",
        "AES256-GCM-SHA384",
    ]
    response = session.get(TLS_API)
    r_cipher_suite = [value for _, value in enumerate(response.json["tls"]["ciphers"])]

    assert "TLS_RSA_WITH_AES_128_CBC_SHA256" in r_cipher_suite
    assert "TLS_RSA_WITH_AES_256_CBC_SHA256" in r_cipher_suite
    assert "TLS_RSA_WITH_AES_128_GCM_SHA256" in r_cipher_suite
    assert "TLS_RSA_WITH_AES_256_GCM_SHA384" in r_cipher_suite


def test_custom_request_header(session):
    session.headers = {"user-agent": "request_curl"}
    response = session.get(TLS_API)

    assert "user-agent: request_curl" in "".join(response.json["http1"]["headers"])


def test_request_form_data(session):
    data = {"key": "value"}
    response = session.post(HTTP_BIN_API + "/post", data=data)

    assert response.json["form"] == data


def test_request_json_body(session):
    _json = {"key": "value"}
    response = session.post(HTTP_BIN_API + "/post", json=_json)

    assert response.json["json"] == _json


def test_request_url_params(session):
    params = {"key": "value"}
    response = session.get(HTTP_BIN_API + "/get", params=params)

    assert "key=value" in response.url


def test_session_cookies_add(session):
    session.add_cookie("a", "b", "c")
    assert len(session.cookies) >= 0
    assert session.cookies["a"] == "b"


def test_session_cookies_request(session):
    session.get("https://google.com")
    assert len(session.cookies) >= 0
    session.get(HTTP_BIN_API)
    assert len(session.cookies) >= 0
    session.get(TLS_API)
    assert len(session.cookies) >= 0


def test_curl_reset(session):
    session.headers = {"user-agent": "test_1"}
    response = session.get(TLS_API)
    assert "user-agent: test_1" in "".join(response.json["http1"]["headers"])

    session.headers = {"user-agent": "test_2"}
    response = session.get(TLS_API)
    assert "user-agent: test_1" not in "".join(response.json["http1"]["headers"])
    assert "user-agent: test_2" in "".join(response.json["http1"]["headers"])

    response = session.post(TLS_API, json={"key": "value"})
    assert "application/json" in "".join(response.json["http1"]["headers"])

    response = session.post(TLS_API, data={"key": "value"})
    assert "application/json" not in "".join(response.json["http1"]["headers"])

    response = session.post(TLS_API, data={"key": "value"}, http2=True)
    assert response.json.get("http_version") == "h2"


def test_debug(session):
    response = session.get(TLS_API, debug=True)

    assert response.status_code == 200


def test_response_header(session):
    response = session.get(HTTP_BIN_API)

    assert isinstance(response.headers, CaseInsensitiveDict)
    assert isinstance(response.headers["content-type"], str)


def test_with_chrome_fp(session):
    session.http2 = True
    session.cipher_suite = CHROME_CIPHER_SUITE
    session.headers = CHROME_HEADERS

    response = session.get(TLS_API)

    assert response.json["user_agent"] == CHROME_UA


def test_response_cookies(session):
    response = session.get(GOOGLE)

    assert len(response.text) > 0
    assert len(response.cookies) > 0


def test_brotli_content_encoding(session):
    session.headers = CHROME_HEADERS
    session.http2 = True
    session.cipher_suite = CHROME_CIPHER_SUITE

    response = session.get(BROWSER_LEAKS)
    assert len(response.text) > 0
