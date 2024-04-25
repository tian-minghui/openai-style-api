
# openai-style-api


 ***本人精力有限，某些模型更新可能无法及时更新，如果遇到问题请提issue，也欢迎有兴趣的大佬提PR***

## 用途
屏蔽不同大模型API的差异，统一用openai api标准格式使用大模型, 也可以用来做api-key的二次分发管理; 配置化管理不同大模型调用参数，让你在使用大模型的时候只需关注 api-key 和 messages

## 功能

- [x] 支持多种大模型，当前已支持
  - [x] openai
  - [x] azure open ai
  - [x] claude-api 【api申请在等待列表，暂未测试】
  - [x] claude-web (将web端功能封装成openai api)
  - [x] 智谱ai
  - [x] kimi
  - [x] bingchat(copilot)
  - [ ] 百度文心一言
  - [x] 讯飞星火
  - [x] gemini
  - [x] 通义千问
  - [ ] ...
- [x] 支持stream方式调用
- [x] 支持open ai的第三方代理服务，比如openai-sb等
- [x] 支持在线更新配置 `http://0.0.0.0:8090/`（这个前端页面和交互完全是用gpt写的 哈哈）
- [x] 支持负载均衡，一个key可轮训/随机/并行等访问多个模型
- [x] 支持按照model_name进行路由

**更新日志**

2024-04-03
- 支持通义千问
- 优化异常处理


## 部署方式

**项目的核心配置依赖model-config.json文件，若是没有model-config.json，默认会使用model-config-default.json启动，这时虽然能启动起来，但是因为api-key等没有配置，无法调用成功。**

### Docker

本地新建一个model-config.json文件，根据下边配置文件示例，进行配置， 然后运行以下命令

    docker pull tianminghui/openai-style-api

    docker run -d -p 8090:8090 --name openai-style-api\
    -e ADMIN-TOKEN=admin \
    -v /path/to/your/model-config.json:/app/model-config.json \
    tianminghui/openai-style-api

`/path/to/your/model-config.json` 替换成你自己的本地路径

### Docker compose
clone本项目，或者下载项目中的`docker-compose.yml`文件，修改其中的`./model-config.json`路径, 然后运行以下命令

    docker-compose up -d


### 本地部署
1. `git clone https://github.com/tian-minghui/openai-style-api.git` 拉取项目代码
2. `cp model-config-default.json model-config.json`  并按需修改配置文件model-config.json
3.  `pip install -r  requirements.txt` 
4. 运行 `python open-api.py`


## 配置说明
model-config.json 配置文件简单示例

```
    [
        {
            "token": "f2b7295fc440db7f",
            "type": "azure",  // azure openai 模型
            "config": {
                "api_base": "https://xxxx.openai.azure.com/",
                "deployment_id": "gpt-35-turbo",
                "api_version": "2023-05-15",
                "api_key": "xxxxxx",
                "temperature": 0.8
            }
        }
    ]
```
- 整个文件是一个json list，可以配置多个模型，只要token不重复就行
- token 自定义的token，后续在请求的时候拿着这个token来请求
- type 类型，表示以下config中的配置是那个模型的，比如 openai，通义千问
- config， 配置openai的api_base, api_key, model等， 针对不用模型有不同的配置（下边有配置示例，更详细配置可以看代码）， 此处的配置优先于客户端请求中的配置，比如"temperature": 0.8,  会覆盖请求中的temperature（这里的想法是可以针对同一个模型，调整不同参数，映射成一个新模型）

## 使用方式

### curl

    curl http://localhost:8090/v1/chat/completions \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer f2b7295fc440db7f" \
          -d '{
            "messages": [
              {
                "role": "system",
                "content": "You are a helpful assistant."
              },
              {
                "role": "user",
                "content": "Hello!"
              }
            ]
          }'

### openai库调用

openai<1.0.0 使用如下方式

    import openai

    openai.api_key = "f2b7295fc440db7f"
    openai.api_base = "http://localhost:8090/v1"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
    print(completion.choices[0].message.content)


openai>=1.0.0使用以下方式调用
    
    import os
    from openai import OpenAI

    client = OpenAI(
        # This is the default and can be omitted
        api_key='kimi-GxqT3BlbkFJj',
        base_url = 'http://localhost:8090/v1'
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo",
    )

    print(chat_completion.choices[0].message.content)

### 第三方应用

[ChatGPT Next Web](https://github.com/Yidadaa/ChatGPT-Next-Web)
![Alt text](img/image.png)

## 配置示例
    [
    {
        "token": "f2b7295fc440db7f",
        "type": "azure",  // azure openai 模型
        "config": {
            "api_base": "https://xxxx.openai.azure.com/",
            "deployment_id": "gpt-35-turbo",
            "api_version": "2023-05-15",
            "api_key": "xxxxxx",
            "temperature": 0.8
        }
    },
    {
        "token": "GxqT3BlbkFJj",
        "type": "openai", // openai 模型
        "config": {
            "api_base": "https://api.openai.com/v1/",
            "api_key": "sk-xxxxxx",
            "model": "gpt-3.5-turbo"
        }
    },
    {
        "token": "sb-ede1529390cc",
        "type": "proxy",  // openai 代理 
        "config": {
            "api_base": "https://api.openai-sb.com/v1/",
            "api_key": "sb-xxxxxx",
            "model": "gpt-3.5-turbo"
        }
    },
    {
        "token": "c115c8f5082",
        "type": "claude-web",  // claude-web 
        "config": {
            "cookie": "xxxxxx",
            "proxies": {
                "https": "http://localhost:7890"
            },
            "conversation_id": "xxxxxx",
            "prompt": "The information in [] is the context of the conversation. Please ignore the JSON format of the context during the conversation and answer the user's latest conversation: {newMessage} \n {history}",
            "single_conversation": true
        }
    },
    {
        "token": "7c7aa4a3549f5",
        "type": "zhipu-api",  // 智谱API
        "config": {
            "api_key": "xxxxxx",
            "model": "chatglm_lite",
            "temperature": 0.8,
            "top_p": 0.7
        }
    },
    {
        "token": "7c7aa4a3549f11",
        "type": "xunfei-spark-api", // 讯飞星火API
        "config": {
            "app_id": "xxxx",
            "api_key": "xxxx",
            "api_secret": "xxxxxx",
            "api_model_version": "v2.0",
            "top_k": 5
        }
    },
    {
        "token": "7c7aa4a3549f12",
        "type": "router", // 路由  可以包含多个模型进行负载均衡
        "config": {
            "router_strategy": "round-robin", // 路由策略  round-robin 轮询   random 随机
            "token_pool": [   // 路由的token池
                "7c7aa4a3549f11",
                "7c7aa4a3549f5"
            ]
        }
    },
    {
        "token": "7c7aa4a3549f13",
        "type": "model-name-router", //根据req中的modelname进行路由, 可以方便的结合ChatGPT-Next-Web
        "config": {
            "model-2-token": {   // 路由的token池
                "spark-api-v2.0":"7c7aa4a3549f11",
                "chatglm_lite": "7c7aa4a3549f5",
                "router-round-robin": "7c7aa4a3549f12"
            }
        }
    },
    {
        "token": "gemini-7c7aa4a3549f5",
        "type": "gemini",   // gemini
        "config": {
            "api_key": "xxxxx",
            "proxies": {
                "https": "http://localhost:7890"
            }
        }
    },
    {
        "token": "bing-7c7aa4a3549f5",  // 必应
        "type": "bing-sydney",
        "config": {
            "cookie": "xxxxx",
            "style": "balanced"
        }
    },
    {
        "token":"qwen-111111xxxx",  // 通义千问
        "type":"qwen",
        "config":{
            "api_key":"sk-xxxxxxxx",
            "model":"qwen-turbo"
        }
    },
    {
        "token": "kimi-GxqT3BlbkFJj1", // kimi
        "type": "openai",    // kimi api与openai相同，因此使用openai就可以
        "config": {
            "api_base": "https://api.moonshot.cn/v1/",
            "api_key": "sk-xxxxxx",
            "model": "moonshot-v1-8k"
        }
    }
    ]


## 项目部分代码来自于以下开源项目，感谢🙏
 - https://github.com/vsakkas/sydney.py
 - https://github.com/suqingdong/sparkapi