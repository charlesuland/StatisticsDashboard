import csv
import json
from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os

import pandas as pd
from auth_routes import get_current_user
from database import SessionLocal, get_db
import ml
from models import Dataset, User
from sqlalchemy.orm import Session

router = APIRouter()

ALLOWED_EXTENSIONS = {".txt", ".csv", ".xlsx"}

@router.get("/")
def index():
    return

@router.get("/login")
def loginPage():
    return

@router.post("/login")
def authenticate():
    # need to verify login
    # need to return a JWT
    return


# Note: we can separate these routes out into separate files if we would like to. 


@router.get("/dashboard")
def userDasboard():
    #give the information needed for the user dashboard
    return

# List datasets for current user
@router.get("/dashboard/datasets")
def get_user_datasets(current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
    datasets = db.query(Dataset).filter(Dataset.owner_id == current_user.id).all()
    return {"files": [d.filename for d in datasets]}

async def detect_delimiter(file: UploadFile):
    content = await file.read()
    await file.seek(0)
    sample = content.decode('utf-8', errors='ignore')
    sniffer = csv.Sniffer()
    return sniffer.sniff(sample).delimiter

@router.post("/dashboard/addDataSet")
async def add_user_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check file extension
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Create user-specific uploads folder
    user_folder = os.path.join("uploads", current_user.username)
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, file.filename)

    # Save uploaded file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    await file.seek(0)

    # Read file into DataFrame
    if ext.lower() in {".txt", ".csv"}:
        delimiter = ","  # default
        if ext.lower() == ".txt":
            # Assuming you have a detect_delimiter function
            delimiter = await detect_delimiter(file)
        df = pd.read_csv(file.file, delimiter=delimiter)
    elif ext.lower() == ".xlsx":
        df = pd.read_excel(file.file)
        delimiter = None

    # Basic schema and type checks
    schema_info = {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}

    # Missing value info
    missing_info = df.isnull().sum().to_dict()
    df = df.dropna(how="any")
    if df.shape[0] == 0:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Uploaded file has no rows after cleaning")
    if df.shape[0] > 1_000_000:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Uploaded file too large")

    # Save a basic preprocessing config
    pipeline_config = {
        "columns": list(df.columns),
        "dtypes": schema_info,
        "missing_values": missing_info
    }

    config_folder = os.path.join("configs", current_user.username)
    os.makedirs(config_folder, exist_ok=True)
    config_path = os.path.join(config_folder, file.filename + "_config.json")
    with open(config_path, "w") as f:
        json.dump(pipeline_config, f, indent=4)

    # Save processed DataFrame without encoding step
    processed_path = os.path.join(user_folder, file.filename + "_processed.csv")
    df.to_csv(processed_path, index=False)

    # Remove original raw file
    os.remove(file_path)

    # Save dataset info in database
    try:
        dataset = Dataset(filename=file.filename, owner_id=current_user.id)
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
    except Exception as e:
        if os.path.exists(processed_path):
            os.remove(processed_path)
        if os.path.exists(config_path):
            os.remove(config_path)
        raise HTTPException(status_code=500, detail=f"Failed to save dataset record: {e}")

    return {
        "filename": file.filename,
        "message": "File uploaded and processed successfully",
        "delimiter": delimiter,
        "schema": schema_info,
        "missing_values": missing_info,
        "config_file": config_path,
        "processed_file": processed_path
    }

@router.post("/dashboard/modelevaluation")
async def modelEval(request: Request, current_user: User = Depends(get_current_user)):
    # get necessary information from request
        # need which model and which dataset
    #perform necessary python and sklearn calcualations
    # return that data
    # how do we want to visualize it?
    body = await request.json()
    filename = body["filename"]
    target = body["target"]
    features = body["features"]
    test_split = body["test_split"]
    model = body["model"]

    file_path = os.path.join("uploads", current_user.username, filename + "_processed.csv")
    df = pd.read_csv(file_path)
    manager = ml.models[model](df, test_split)
    result = manager.train(target, features)
    print(result)
    return 

@router.get("/dashboard/datasets/columns")
def get_columns(
    filename: str = Query(..., description="Name of the dataset file"),
    current_user: User = Depends(get_current_user)
):
    user_folder = os.path.join("uploads", current_user.username)
    file_path = os.path.join(user_folder, filename + "_processed.csv")

    print(filename)
    print(file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    try:
        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
        return {"columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")

