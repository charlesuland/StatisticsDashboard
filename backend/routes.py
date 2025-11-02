import csv
from fastapi import APIRouter, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os

import pandas as pd
import ml

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

@router.get("/dashboard/datasets")
def userDatasets():
    print("routed up")
    files = []
    for filename in os.listdir("uploads"):
        files.append(filename)
    return {"files": files}
async def detect_delimiter(file: UploadFile):
    content = await file.read()
    await file.seek(0)
    sample = content.decode('utf-8', errors='ignore')
    sniffer = csv.Sniffer()
    return sniffer.sniff(sample).delimiter

@router.post("/dashboard/addDataSet")
async def addUserDataSet(file: UploadFile = File(...)):
    # Check file extension
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

    # Create user-specific uploads folder
    user_folder = os.path.join("uploads")
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, file.filename)

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    await file.seek(0)  # Reset file pointer for reading

    # Read file into DataFrame
    if ext.lower() in {".txt", ".csv"}:
        delimiter = ","  # default
        if ext.lower() == ".txt":
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
    num_rows = df.shape[0]
    num_columns = len(df.columns.tolist())
    if df.shape[0] == 0:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Uploaded file has no rows after cleaning")
    if df.shape[0] > 1_000_000:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail="Uploaded file too large")


    # Save a basic preprocessing config (for demonstration)
    pipeline_config = {
        "columns": list(df.columns),
        "dtypes": schema_info,
        "missing_values": missing_info
    }
    df_encoded = df.copy()
    
    for col in df_encoded.select_dtypes(include='object').columns:
        try:
            # Try to convert strings that are numeric
            df_encoded[col] = pd.to_numeric(df_encoded[col])
        except:
            # Convert non-numeric strings to categorical codes
            df_encoded[col] = pd.Categorical(df_encoded[col]).codes
    
    df = df_encoded
    import json
    config_path = os.path.join("configs", file.filename + "_config.json")
    with open(config_path, "w") as f:
        json.dump(pipeline_config, f, indent=4)

    df.to_csv(os.path.join(user_folder, file.filename + "_processed.csv"), index=False)
    os.remove(file_path)
    return {
        "filename": file.filename,
        "message": "File uploaded and processed successfully",
        "delimiter": delimiter,
        "schema": schema_info,
        "missing_values": missing_info,
        "config_file": config_path
    }

@router.post("/dashboard/modelevaluation")
async def modelEval(request: Request):
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

    file_path = os.path.join("uploads", filename)
    df = pd.read_csv(file_path)
    manager = ml.models[model](df, test_split)
    result = manager.train(target, features)
    print(result)
    return 

@router.get("/dashboard/datasets/columns")
def get_columns(filename: str = ""):
    file_path = os.path.join("uploads", filename)
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    try:
        
        
        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
        return {"columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")
