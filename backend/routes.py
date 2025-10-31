from fastapi import APIRouter, File, UploadFile
import os

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
    return

@router.post("/dashboard/addDataSet")
async def addUserDataSet(file: UploadFile = File(...)):
    os.makedirs("uploads", exist_ok=True)
    #ultimately the file path needs to include the username
    # this is just showing the functionality of adding a file
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return

@router.post("/dashboard/modelEvaluation")
def modelEval():
    #perform necessary python and sklearn calcualations
    # return that data
    # how do we want to visualize it?
    return

