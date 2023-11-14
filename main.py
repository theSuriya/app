import uvicorn
from fastapi import FastAPI,File,UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
from PIL import Image
from io import BytesIO
from keras.models import load_model
from fastapi import Request
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend")


api_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the model relative to the 'api' directory
model_path = os.path.join(api_directory, 'my model', 'yoga-modelv2.h5')

model = load_model(model_path)

class_name = ['Bridge Pose','Child-Pose','CobraPose','Downward Dog pose','Pigeon pose','Standing Mountain Pose','Tree Pose','Triangle Pose','Warrior Pose']



@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/ping')
async def check():
    return "Hello world"


def read_file_as_image(data):
    img = Image.open(BytesIO(data)).resize((224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    return img_array

@app.post('/predict')
async def prediction(file: UploadFile = File(...)):

     img = read_file_as_image(await file.read())
     img = np.expand_dims(img, axis=0)

     predicted =  model.predict(img)
     result = class_name[np.argmax(predicted[0])]
     confidence = np.max(predicted[0])

     return{
         'class': result,
         'confidence':round(confidence * 100, 1)
     }


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8501)