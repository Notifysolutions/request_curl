from typing import Dict, List

CHROME_UA: str = "".join(
    [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1)",
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    ]
)

CHROME_HEADERS: Dict[str, str] = {
    "sec-ch-ua": ' Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": CHROME_UA,
    "Accept": "".join(
        [
            "text/html,application/xhtml+xml,application/xml;q=0.9,",
            "image/avif,image/webp,image/apng,*/*;q=0.8,",
            "application/signed-exchange;v=b3;q=0.9",
        ]
    ),
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}

CHROME_CIPHER_SUITE: List[str] = [
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
