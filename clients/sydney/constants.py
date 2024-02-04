USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91"

CREATE_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://copilot.microsoft.com/",
    "Sec-Ch-Ua": '"Microsoft Edge";v="120", "Chromium";v="120", "Not?A_Brand";v="8"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": USER_AGENT,
    "X-Edge-Shopping-Flag": "0",
}

CHATHUB_HEADERS = {
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "Upgrade",
    "Origin": "https://copilot.microsoft.com",
    "Pragma": "no-cache",
    "User-Agent": USER_AGENT,
}

KBLOB_HEADERS = {
    "Accept": "image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Content-Type": "multipart/form-data",
    "Referer": "https://copilot.microsoft.com/",
    "Sec-Ch-Ua": '"Microsoft Edge";v="120", "Chromium";v="120", "Not?A_Brand";v="8"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": USER_AGENT,
    "X-Edge-Shopping-Flag": "0",
}

BUNDLE_VERSION = "1.1381.12"

BING_CREATE_CONVERSATION_URL = f"https://edgeservices.bing.com/edgesvc/turing/conversation/create?bundleVersion={BUNDLE_VERSION}"
BING_GET_CONVERSATIONS_URL = "https://copilot.microsoft.com/turing/conversation/chats"
BING_CHATHUB_URL = "wss://sydney.bing.com/sydney/ChatHub"
BING_KBLOB_URL = "https://copilot.microsoft.com/images/kblob"
BING_BLOB_URL = "https://copilot.microsoft.com/images/blob?bcid="

DELIMETER = "\x1e"  # Record separator character.
