from fastapi import FastAPI, HTTPException, Query
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
def get_paginated_data(
    dataset_id: str, 
    page: int = Query(default=1, ge=1),      # Must be greater than or equal to 1
    size: int = Query(default=100, le=500)   # Must be less than or equal to 500 rows
):
    if dataset_id not in DB_FILES:
        raise HTTPException(status_code=404, detail="Dataset not found.")
        
    db_path = DB_FILES[dataset_id]
    
    offset = (page - 1) * size
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT COUNT(*) FROM {dataset_id}")
        total_records = cursor.fetchone()[0]
        
        cursor.execute(
            f"SELECT * FROM {dataset_id} ORDER BY Timestamp DESC LIMIT ? OFFSET ?",
            (size, offset)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return {
            "metadata": {
                "current_page": page,
                "page_size": size,
                "total_records": total_records,
                "total_pages": (total_records + size - 1) // size  # Clean ceiling division
            },
            "records": [dict(row) for row in rows]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database pagination error: {str(e)}")    

@app.get("/images/{image_name}")
def get_image(image_name: str):
    
    image_path = os.path.join(IMAGE_DIR, image_name)
    
    if not os.path.exists(image_path) or not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image not found.")
    
    return FileResponse(image_path)
