import request_curl
from request_curl import CHROME_CIPHER_SUITE, CHROME_HEADERS, CHROME_UA
from request_curl.dict import CaseInsensitiveDict

TLS_API: str = "https://tls.peet.ws/api/all"
HTTP_BIN_API: str = "https://httpbin.org"


def test_context_manager():
    with request_curl.Session() as session:
        r = session.get(HTTP_BIN_API + "/get")
        assert r.status_code == 200


def test_http_version():
    session = request_curl.Session(http2=True)
    response = session.get(TLS_API).json
    assert response.get("http_version") == "h2"

    session = request_curl.Session(http2=False)
    response = session.get(TLS_API).json
    assert response.get("http_version") == "HTTP/1.1"


def test_request_methods():
    session = request_curl.Session()

    assert session.get(TLS_API).json["method"] == "GET"
    assert session.post(TLS_API).json["method"] == "POST"
    assert session.options(TLS_API).json["method"] == "OPTIONS"
    assert session.delete(TLS_API).json["method"] == "DELETE"
    assert session.put(TLS_API).json["method"] == "PUT"


def test_response_object_props():
    session = request_curl.Session()

    for url in [TLS_API, HTTP_BIN_API + "/get"]:
        response = session.get(url)

        assert isinstance(response.status_code, int) and response.status_code >= 0
        assert isinstance(response.content, bytes) and len(response.content) > 0
        assert isinstance(response.text, str) and len(response.text) > 0
        assert isinstance(response.json, dict) and len(response.json) > 0
        assert isinstance(response.url, str) and len(response.url) > 0


def test_custom_cipher_suite():
    cipher_suite = [
        "AES128-SHA256",
        "AES256-SHA256",
        "AES128-GCM-SHA256",
        "AES256-GCM-SHA384",
    ]
    session = request_curl.Session(cipher_suite=cipher_suite)
    response = session.get(TLS_API)

    r_cipher_suite = [value for _, value in enumerate(response.json["tls"]["ciphers"])]

    assert "TLS_RSA_WITH_AES_128_CBC_SHA256" in r_cipher_suite
    assert "TLS_RSA_WITH_AES_256_CBC_SHA256" in r_cipher_suite
    assert "TLS_RSA_WITH_AES_128_GCM_SHA256" in r_cipher_suite
    assert "TLS_RSA_WITH_AES_256_GCM_SHA384" in r_cipher_suite


def test_custom_request_header():
    session = request_curl.Session(headers={"user-agent": "request_curl"})
    response = session.get(TLS_API)

    assert "user-agent: request_curl" in "".join(response.json["http1"]["headers"])


def test_request_form_data():
    data = {"key": "value"}
    session = request_curl.Session()
    response = session.post(HTTP_BIN_API + "/post", data=data)

    assert response.json["form"] == data


def test_request_json_body():
    _json = {"key": "value"}
    session = request_curl.Session()
    response = session.post(HTTP_BIN_API + "/post", json=_json)

    assert response.json["json"] == _json


def test_request_url_params():
    params = {"key": "value"}
    session = request_curl.Session()
    response = session.get(HTTP_BIN_API + "/get", params=params)

    assert "key=value" in response.url


def test_session_cookies_add():
    session = request_curl.Session(http2=True, headers={})
    session.add_cookie("a", "b", "c")
    assert len(session.cookies) >= 0
    assert session.cookies["a"] == "b"


def test_session_cookies_request():
    session = request_curl.Session(http2=True, headers={})
    session.get("https://google.com")
    assert len(session.cookies) >= 0
    session.get(HTTP_BIN_API)
    assert len(session.cookies) >= 0
    session.get(TLS_API)
    assert len(session.cookies) >= 0


def test_curl_reset():
    session = request_curl.Session(http2=False, headers={"user-agent": "test_1"})
    response = session.get(TLS_API)
    assert "user-agent: test_1" in "".join(response.json["http1"]["headers"])

    response = session.get(TLS_API, headers={"user-agent": "test_2"})
    assert "user-agent: test_1" not in "".join(response.json["http1"]["headers"])
    assert "user-agent: test_2" in "".join(response.json["http1"]["headers"])

    response = session.post(TLS_API, json={"key": "value"})
    assert "application/json" in "".join(response.json["http1"]["headers"])

    response = session.post(TLS_API, data={"key": "value"})
    assert "application/json" not in "".join(response.json["http1"]["headers"])

    response = session.post(TLS_API, data={"key": "value"}, http2=True)
    assert response.json.get("http_version") == "h2"


def test_debug():
    session = request_curl.Session(http2=True, headers={"user-agent": "test_1"})
    response = session.get(TLS_API, debug=True)

    assert response.status_code == 200


def test_response_header():
    session = request_curl.Session(http2=True, headers={"user-agent": "test_1"})
    response = session.get(HTTP_BIN_API)

    assert isinstance(response.headers, CaseInsensitiveDict)
    assert isinstance(response.headers["content-type"], str)


def test_with_chrome_fp():
    session = request_curl.Session(
        http2=True, cipher_suite=CHROME_CIPHER_SUITE, headers=CHROME_HEADERS
    )

    response = session.get(TLS_API)

    assert response.json["user_agent"] == CHROME_UA


def test_response_cookies():
    session = request_curl.Session()
    response = session.get("https://google.com")

    assert len(response.cookies) > 0
