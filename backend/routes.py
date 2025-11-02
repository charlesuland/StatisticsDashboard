from fastapi import APIRouter, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os

import pandas as pd
from ml.ml_manager import MLManager


router = APIRouter()

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

@router.post("/dashboard/addDataSet")
async def addUserDataSet(file: UploadFile = File(...)):

    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in [".txt", ".csv", ".xlsx"]:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed types: {', '.join([".txt", ".csv", ".xlsx"])}")


    os.makedirs("uploads", exist_ok=True)

    
    
    #ultimately the file path needs to include the username
    # this is just showing the functionality of adding a file
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return {"filename": file.filename, "message": "file uploaded successfully"}

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
    file_path = os.path.join("uploads", filename)
    df = pd.read_csv(file_path)
    manager = MLManager(df, test_split)
    result = manager.train_linear_regression(target, features)
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
