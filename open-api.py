import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.routing import APIRouter
from core.adapters.base import ModelAdapter
from core.protocol import ChatCompletionRequest, ChatCompletionResponse
from typing import Iterator, Optional
from core.adapter_manager import getModelByKey
from loguru import logger


router = APIRouter()


def create_app():
    """ create fastapi app server """
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
        HTTPBearer(auto_error=False)),
):
    logger.info(f"auth: {auth}")
    if auth and auth.credentials:
        token = auth.credentials
        model = getModelByKey(token)
        if model is not None:
            return model
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


def convert(resp: Iterator[ChatCompletionResponse]):
    for response in resp:
        yield f"data: {response.model_dump_json(exclude_none=True)}\n\n"
    yield "data: [DONE]\n\n"


@router.post("/v1/chat/completions")
def create_chat_completion(request: ChatCompletionRequest, model: ModelAdapter = Depends(check_api_key)):
    logger.info(f"request: {request},  model: {model}")
    resp = model.chat_completions(request)
    if request.stream:
        return StreamingResponse(convert(resp), media_type="text/event-stream")
    else:
        openai_response = next(resp)
        return JSONResponse(content=openai_response.model_dump(exclude_none=True))


def run(port=8090, log_level="info", prefix=""):
    import uvicorn
    app = create_app()
    app.include_router(router, prefix=prefix)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level=log_level)


if __name__ == '__main__':
    run()
