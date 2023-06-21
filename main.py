from python_script import main
from fastapi import FastAPI, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from queue import Queue
import asyncio
from fastapi.responses import StreamingResponse

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://www.zeilertech.com",
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

queue = Queue()

class BaseCallbackHandler:
    def on_llm_new_token(self, token):
        queue.put(token)

@app.post("/run_script")
async def run_script(background_tasks: BackgroundTasks, item: Item):
    handler = BaseCallbackHandler()
    background_tasks.add_task(main, item.input, handler)
    return Response(status_code=202)

@app.get("/stream")
async def stream() -> StreamingResponse:
    async def event_stream():
        while True:
            token = queue.get()
            yield f"data:{token}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
