from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.websockets import WebSocketState
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent.pm_agent import PMAgent

app = FastAPI(title="AI PM Agent", version="1.0.0")

agents: dict[str, PMAgent] = {}


def get_or_create_agent(session_id: str) -> PMAgent:
    if session_id not in agents:
        agents[session_id] = PMAgent(session_id)
    return agents[session_id]


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ModeSwitchRequest(BaseModel):
    mode: str
    session_id: str = "default"


@app.get("/api")
def api_info():
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


@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")


@app.post("/chat")
def chat(request: ChatRequest):
    agent = get_or_create_agent(request.session_id)
    response = agent.chat(request.message)
    return {
        "response": response,
        "mode": agent.mode,
        "use_mock": agent.use_mock,
    }


@app.post("/mode")
def switch_mode(request: ModeSwitchRequest):
    agent = get_or_create_agent(request.session_id)
    agent.set_mode(request.mode)
    return {"mode": agent.mode, "message": f"已切换到 {agent.mode} 模式"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str = Query("default")):
    await websocket.accept()
    agent = get_or_create_agent(session_id)

    history_count = len(agent.memory.get_chat_history())
    welcome = (
        f"👋 你好！我是「老钱」，你的 AI 产品经理。\n\n"
        f"**当前模式**: {agent.mode.upper()}\n"
        f"**AI 状态**: {'✅ AI 已连接' if not agent.use_mock else '⚠️ Mock 模式'}\n"
        f"**历史消息**: {history_count} 条\n\n"
        f"命令: `/pm` 产品模式 | `/dev` 开发模式 | `/project <名>` 创建项目\n\n"
        f"来，跟我说说你的产品想法吧～"
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
        print(f"Session {session_id} disconnected (agent preserved)")
    except Exception as e:
        print(f"WebSocket error for {session_id}: {e}")
    finally:
        try:
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close()
        except Exception:
            pass

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
