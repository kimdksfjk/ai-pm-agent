from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from pydantic import BaseModel

from agent.pm_agent import PMAgent

app = FastAPI(title="AI PM Agent", version="1.0.0")

agents: dict[str, PMAgent] = {}


def get_or_create_agent(client_id: str) -> PMAgent:
    if client_id not in agents:
        agents[client_id] = PMAgent()
    return agents[client_id]


class ChatRequest(BaseModel):
    message: str
    client_id: str = "default"


class ModeSwitchRequest(BaseModel):
    mode: str
    client_id: str = "default"


@app.get("/")
def read_root():
    return {
        "service": "AI PM Agent",
        "version": "1.0.0",
        "modes": ["pm", "dev"],
        "commands": ["/pm", "/dev", "/project", "/project <name>"],
        "endpoints": {
            "websocket": "ws://127.0.0.1:8000/ws",
            "chat_post": "POST /chat",
        },
    }


@app.post("/chat")
def chat(request: ChatRequest):
    agent = get_or_create_agent(request.client_id)
    response = agent.chat(request.message)
    return {
        "response": response,
        "mode": agent.mode,
        "use_mock": agent.use_mock,
    }


@app.post("/mode")
def switch_mode(request: ModeSwitchRequest):
    agent = get_or_create_agent(request.client_id)
    agent.set_mode(request.mode)
    return {"mode": agent.mode, "message": f"已切换到 {agent.mode} 模式"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(id(websocket))
    agent = get_or_create_agent(client_id)

    welcome = (
        f"你好！我是「老钱」，你的 AI 产品经理。\n"
        f"当前模式: {agent.mode.upper()}\n"
        f"运行模式: {'Mock（配置 API Key 以启用 AI）' if agent.use_mock else 'AI 已连接'}\n"
        f"命令: /pm 产品模式 | /dev 开发者模式 | /project 查看项目 | /project <名> 创建项目\n"
        f"来，跟我说说你的需求吧～"
    )
    await websocket.send_text(welcome)

    try:
        while True:
            data = await websocket.receive_text()

            if not data.strip():
                continue

            response = agent.chat(data)

            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(response)
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
    except Exception as e:
        print(f"WebSocket error for {client_id}: {e}")
    finally:
        agents.pop(client_id, None)
        try:
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close()
        except Exception:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
