from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from python_script import main
from pydantic import BaseModel
from queue import Queue
import json
import asyncio
from pydantic import BaseModel, ValidationError
from langchain.callbacks.base import AsyncCallbackHandler

class Item(BaseModel):
    input: str

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://www.zeilertech.com",
    "https://www.profhastings.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    input: str

queue = asyncio.Queue()

class MyCustomAsyncHandler(AsyncCallbackHandler):
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(f"Async handler being called: token: {token}")
        await queue.put(token)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        print("Waiting for client data...")
        data = await websocket.receive_text()
        print(f"Received data: {data}")
        try:
            item = Item(**json.loads(data))
            print(f"Received item: {item.input}")
        except ValidationError as e:
            print(f"Error: {e}")
            continue
        handler = MyCustomAsyncHandler()
        task = asyncio.create_task(main(item.input, handler, queue))
        print("Started task")
        print(task.done)
        while True:
            token = await queue.get()
            print(token)
            if token == "DONE":
                print("Done sending response")
                break
            await websocket.send_text(token)
