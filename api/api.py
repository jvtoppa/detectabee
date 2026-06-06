from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
import os
import sqlite3

app = FastAPI()

IMAGE_DIR = "./images"
DB_FILES = {
    "camera_feed": "/home/rpi-abelha/detectabee/data/camera_feed.db",
    "station_feed": "/home/rpi-abelha/detectabee/data/station_feed.db"
}

@app.get("/data/{dataset_id}")
def get_db_data(dataset_id: str, limit: int = 100):
    
    if dataset_id not in DB_FILES:
        raise HTTPException(status_code=404, detail="Dataset not found.")
        
    db_path = DB_FILES[dataset_id]
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {dataset_id} ORDER BY Timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database reading error: {str(e)}")
    

@app.get("/images/{image_name}")
def get_image(image_name: str):
    
    image_path = os.path.join(IMAGE_DIR, image_name)
    
    if not os.path.exists(image_path) or not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")
    
    return FileResponse(image_path)
