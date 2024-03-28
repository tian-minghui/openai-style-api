import json
from typing import List
from websockets.sync.client import connect as ws_connect
import hmac
import base64
import hashlib
import textwrap
from urllib.parse import urlencode, urlparse
from datetime import datetime
from email.utils import formatdate
from loguru import logger
import uuid


#  https://www.xfyun.cn/doc/spark/Web.html#_1-%E6%8E%A5%E5%8F%A3%E8%AF%B4%E6%98%8E
#  https://github.com/suqingdong/sparkapi/tree/main

MODEL_MAP = {
    "v1.5": {
        "domain": "general",
        "url": "wss://spark-api.xf-yun.com/v1.1/chat",
    },
    "v2.0": {
        "domain": "generalv2",
        "url": "wss://spark-api.xf-yun.com/v2.1/chat",
    },
    "v3.0": {
        "domain": "generalv3",
        "url": "wss://spark-api.xf-yun.com/v3.1/chat",
    },
    "v3.5": {
        "domain": "generalv3.5",
        "url": "wss://spark-api.xf-yun.com/v3.5/chat",
    },
}


def generate_rfc1123_date():
    """
    Generate a RFC 1123 compliant date string.

    """
    current_datetime = datetime.now()
    timestamp = current_datetime.timestamp()
    return formatdate(timeval=timestamp, localtime=False, usegmt=True)

    # the same as:
    # datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S %Z')


def get_wss_url(api_url, api_secret, api_key):
    """
    Generate auth params for API request.
    """
    api_host = urlparse(api_url).netloc
    api_path = urlparse(api_url).path

    # step1: generate signature
    rfc1123_date = generate_rfc1123_date()
    signature_origin = textwrap.dedent(
        f"""
        host: {api_host}
        date: {rfc1123_date}
        GET {api_path} HTTP/1.1
    """
    ).strip()
    signature_sha = hmac.new(
        api_secret.encode(), signature_origin.encode(), digestmod=hashlib.sha256
    ).digest()
    signature_sha_base64 = base64.b64encode(signature_sha).decode()

    # step2: generate authorization
    authorization_payload = {
        "api_key": api_key,
        "algorithm": "hmac-sha256",
        "headers": "host date request-line",
        "signature": signature_sha_base64,
    }
    authorization_origin = ", ".join(
        f'{k}="{v}"' for k, v in authorization_payload.items()
    )
    authorization = base64.b64encode(authorization_origin.encode()).decode()

    # step3: generate wss url
    payload = {"authorization": authorization, "date": rfc1123_date, "host": api_host}
    url = api_url + "?" + urlencode(payload)
    # print(f'wss url: {url}')
    return url


class SparkAPI(object):
    def __init__(
        self, app_id: str, api_key: str, api_secret: str, api_model: str, **kwargs
    ):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_model = api_model

    def create_wss_connection(self):
        api_url = MODEL_MAP[self.api_model]["url"]
        wss_url = get_wss_url(api_url, self.api_secret, self.api_key)
        return ws_connect(wss_url)

    def build_query(self, messages, **kwargs):
        query = {
            "header": {"app_id": self.app_id, "uid": str(kwargs.get("uid", 110))},
            "parameter": {
                "chat": {
                    "domain": MODEL_MAP[self.api_model]["domain"],
                    "temperature": kwargs.get("temperature", 0.5),
                    "max_tokens": kwargs.get("max_tokens", 1024),
                    "top_k": kwargs.get("top_k", 4),
                    "chat_id": str(kwargs.get("chat_id", uuid.uuid1())),
                }
            },
            "payload": {"message": {"text": messages}},
        }

        return json.dumps(query, ensure_ascii=False)

    def get_completion(self, prompt: str, **kwargs):
        """get completion from prompt"""
        messages = [{"role": "user", "content": prompt}]
        return self.get_completion_from_messages(messages, **kwargs)

    def get_resp_from_messages(self, messages: List[dict], **kwargs):
        wss = self.create_wss_connection()

        query = self.build_query(messages, **kwargs)
        logger.info(f"query: {query}")
        wss.send(query)
        cnt = 1
        while True:
            res = json.loads(wss.recv())
            logger.info(f"cnt:{cnt}, res:{res}")
            yield res
            cnt += 1
            if res["header"]["status"] == 2:
                break

    def get_completion_from_messages(self, messages: List[dict], **kwargs):
        """
        # 接口为流式返回，此示例为最后一次返回结果，开发者需要将接口多次返回的结果进行拼接展示
        {
            "header":{
                "code":0,
                "message":"Success",
                "sid":"cht000cb087@dx18793cd421fb894542",
                "status":2
            },
            "payload":{
                "choices":{
                    "status":2,
                    "seq":0,
                    "text":[
                        {
                            "content":"我可以帮助你的吗？",
                            "role":"assistant",
                            "index":0
                        }
                    ]
                },
                "usage":{
                    "text":{
                        "question_tokens":4,
                        "prompt_tokens":5,
                        "completion_tokens":9,
                        "total_tokens":14
                    }
                }
            }
        }
        """
        result = self.get_resp_from_messages(messages, **kwargs)
        for res in result:
            yield res["payload"]["choices"]["text"][0]["content"]


if __name__ == "__main__":
    import os

    app_id = os.environ["SPARK_APP_ID"]
    api_key = os.environ["SPARK_API_KEY"]
    api_secret = os.environ["SPARK_APP_SECRET"]
    print(app_id, api_key, api_secret)
    api = SparkAPI(app_id, api_key, api_secret, "v2.0")
    messages = [{"role": "user", "content": "你好"}]
    res = api.get_completion_from_messages(messages)
    print("".join(res))
