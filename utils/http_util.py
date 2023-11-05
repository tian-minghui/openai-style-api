import requests
import json
from loguru import logger

api_timeout_seconds = 300


def post(api_url, headers: dict, params: dict, timeout=api_timeout_seconds):
    resp = None
    try:
        resp = requests.post(
            url=api_url, headers=headers, data=json.dumps(params), timeout=timeout
        )
        if requests.codes.ok != resp.status_code:
            logger.error(f"响应异常：{resp_text(resp)}")
            raise Exception("响应异常：" + resp_text(resp))
        return json.loads(resp.text)
    except Exception as e:
        logger.exception("请求异常", e)
        raise e
    finally:
        logger.debug(
            f"【http.post】 请求url：{api_url}, headers:{headers}, params:{params}, resp:{resp_text(resp)}"
        )


def resp_text(resp):
    resp_str = None
    if resp:
        resp_str = f"status_code:{resp.status_code}: {resp.text}"
    return resp_str


def stream(api_url, headers: dict, params: dict, timeout=api_timeout_seconds):
    resp = None
    try:
        resp = requests.post(
            api_url,
            stream=True,
            headers=headers,
            json=params,
            # data=json.dumps(params),
            timeout=timeout,
        )
        if requests.codes.ok != resp.status_code:
            logger.error(f"响应异常：{resp.text}")
            raise Exception("请求异常")
        return resp
    except Exception as e:
        logger.exception("请求异常", e)
    finally:
        logger.debug(
            f"【http.stream】 请求url：{api_url}, headers:{headers}, params:{params}"
        )
