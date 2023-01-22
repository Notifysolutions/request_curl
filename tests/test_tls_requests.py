import request_curl


def test_request_curl():
    session = request_curl.Session(http2=True, headers={})
    response = session.get("https://google.com")
    assert response.status_code == 200


def test_session_cookies():
    session = request_curl.Session(http2=True, headers={})
    session.add_cookie("a", "b", "c")
    assert len(session.cookies) >= 0

