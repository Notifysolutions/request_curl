import pytest

import request_curl


@pytest.fixture()
def session():
    return request_curl.Session(verify=False)
