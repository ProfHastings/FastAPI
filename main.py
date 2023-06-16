from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import python_script
import gc

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

@app.post("/run_script")
async def run_script(item: Item):
    output = python_script.run_script(item.input)
    return {"output": output}
