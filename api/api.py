from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import os

app = FastAPI()

IMAGE_DIR = "./images"
CSV_FILES = {
    "dataset1": "./data/camera_feed.csv",
    "dataset2": "./data/station_feed.csv"
}

@app.get("/data/{dataset_id}")
def get_csv_data(dataset_id: str):

    if dataset_id not in CSV_FILES:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    
    csv_path = CSV_FILES[dataset_id]
    
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=500, detail="CSV file missing on server.")
    
    df = pd.read_csv(csv_path)
    return df.to_dict(orient="records")

@app.get("/images/{image_name}")
def get_image(image_name: str):
    
    image_path = os.path.join(IMAGE_DIR, image_name)
    
    if not os.path.exists(image_path) or not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")
    
    return FileResponse(image_path)
