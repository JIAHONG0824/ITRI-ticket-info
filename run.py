from fastapi import FastAPI
from gradio_ui import *
import uvicorn

app = FastAPI()

@app.get('/')
async def root():
    return 'Gradio app is running at /gradio', 200

app = gr.mount_gradio_app(app, demo, path='/gradio')
uvicorn.run(app)