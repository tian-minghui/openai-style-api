import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.routing import APIRouter
from pydantic import BaseModel
from adapters.base import ModelAdapter, UDFApiError, serverError
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
from typing import Iterator, List, Optional
from adapters.adapter_factory import get_adapter
from loguru import logger
from config import (
    ModelConfig,
    get_model_config,
    load_model_config,
    get_all_model_config,
    update_model_config,
)
import os
from fastapi.staticfiles import StaticFiles

router = APIRouter()
admin_token = uuid.uuid1()


def create_app():
    """create fastapi app server"""
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


def check_api_key(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
):
    logger.info(f"auth: {auth}")
    if auth and auth.credentials:
        token = auth.credentials
        adaptor = get_adapter_by_token(token)
        if adaptor is not None:
            return adaptor
        logger.warning(f"invalid api key,{token}")
    raise HTTPException(
        status_code=401,
        detail={
            "error": {
                "message": "",
                "type": "invalid_request_error",
                "param": None,
                "code": "invalid_api_key",
            }
        },
    )


def check_admin_token(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
):
    logger.info(f"auth: {auth}")
    if auth and auth.credentials:
        token = auth.credentials
        if token == admin_token:
            return
        logger.warning(f"invalid admin token,{token}")
    raise HTTPException(
        status_code=401,
        detail={
            "error": {
                "message": "",
                "type": "invalid_request_error",
                "param": None,
                "code": "invalid_token",
            }
        },
    )


def convert(first_resp: ChatCompletionResponse, resp: Iterator[ChatCompletionResponse]):
    yield f"data: {first_resp.model_dump_json(exclude_none=True)}\n\n"
    yield from (
        f"data: {response.model_dump_json(exclude_none=True)}\n\n" for response in resp
    )
    yield "data: [DONE]\n\n"


def get_adapter_by_token(token: str):
    model_config = get_model_config(token)
    if model_config is not None:
        return get_adapter(model_config.token)


@router.post("/v1/chat/completions")
def create_chat_completion(
    request: ChatCompletionRequest, model: ModelAdapter = Depends(check_api_key)
):
    logger.info(f"request: {request},  model: {model}")
    try:
        resp = model.chat_completions(request)
        if request.stream:
            # 为了让生成器中的异常，在这里被捕获，StreamingResponse中会吞掉异常
            first_respose = next(resp)
            return StreamingResponse(
                convert(first_respose, resp), media_type="text/event-stream"
            )
        else:
            openai_response = next(resp)
            return JSONResponse(content=openai_response.model_dump(exclude_none=True))
    except UDFApiError as ue:
        return JSONResponse(content=ue._message, status_code=ue.http_status)
    except Exception as e:
        logger.exception(e)
        return JSONResponse(content=str(e), status_code=500)


@router.get("/verify")
def admin_token_verify(token=Depends(check_admin_token)):
    return {"success": True}


@router.get("/", response_class=HTMLResponse)
def home():
    html_file = open("./dist/index.html", "r").read()
    return html_file


@router.get("/getAllModelConfig")
def get_all_config(token=Depends(check_admin_token)):
    return JSONResponse(content=get_all_model_config())


class ModelConfigRequest(BaseModel):
    config: str


@router.post("/updateModelConfig")
def update_config(request: List[ModelConfig], token=Depends(check_admin_token)):
    update_model_config(request)
    return {"success": True}


def run(port=8090, log_level="info", prefix=""):
    import uvicorn

    app = create_app()
    app.include_router(router, prefix=prefix)
    app.mount("/static", StaticFiles(directory="dist"), name="static")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level=log_level)


if __name__ == "__main__":
    load_model_config()
    env_token = os.getenv("ADMIN-TOKEN")
    if env_token:
        admin_token = env_token
    run()
