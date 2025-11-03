import csv
import datetime
import json
from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, Query, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os
import io
import matplotlib
from pydantic import BaseModel
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sqlalchemy.orm import Session
import pandas as pd
from auth_routes import get_current_user
from database import SessionLocal, get_db
import ml
from models import Dataset, DefaultModel, Plot, User
from typing import List

router = APIRouter()

# Mapping from frontend model names to SQLAlchemy tables


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
def get_user_datasets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
    # df = df.dropna(how="any")
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
async def model_eval(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    body = await request.json()
    
    # Extract frontend inputs
    filename = body.get("filename")
    target = body.get("target")
    features = body.get("features")
    test_split = body.get("test_split")
    model_name = body.get("model")

    model_params = body.get("params", {})  # hyperparameters

    if not all([filename, target, features, model_name]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Load processed dataset
    file_path = os.path.join("uploads", current_user.username, filename + "_processed.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = pd.read_csv(file_path)

    # Train the model
    if model_name not in ml.models:
        raise HTTPException(status_code=400, detail=f"Invalid model: {model_name}")
        
    try:
        manager = ml.models[model_name](df, test_split, **model_params)
        result = manager.train(target, features)
    except Exception as e:
        return {"success": False, "error": str(e)}

    # Get SQLAlchemy model/table class from mapping
    model_table_class = DefaultModel
    if model_table_class is None:
        raise HTTPException(status_code=400, detail=f"No DB table mapped for model: {model_name}")

    # Save configuration and results to the specific model table
    model_entry = model_table_class(
        user_id=current_user.id,
        dataset=filename,
        model_type=model_name,
        parameters=model_params,
        metrics=result,
        
        created_at=datetime.datetime.utcnow()
    )

    db.add(model_entry)
    db.commit()
    db.refresh(model_entry)

    # Return the result to the frontend


    # find dataset record (create if missing)
    dataset = db.query(Dataset).filter(Dataset.filename == filename, Dataset.owner_id == current_user.id).first()
    if dataset is None:
        # create dataset record if absent (keeps compatibility)
        dataset = Dataset(filename=filename, owner_id=current_user.id)
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

    saved_plots = []

    def _save_fig(name: str, fig):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        img_bytes = buf.read()
        plot = Plot(dataset_id=dataset.id, name=name, image=img_bytes)
        db.add(plot)
        db.commit()
        db.refresh(plot)
        saved_plots.append({"id": plot.id, "name": name})

    # render ROC curve
    try:
        if "roc_curve" in result:
            fpr = result["roc_curve"]["fpr"]
            tpr = result["roc_curve"]["tpr"]
            fig, ax = plt.subplots()
            ax.plot(fpr, tpr, label=f"ROC (AUC={result.get('roc_auc', 'n/a')})")
            ax.plot([0, 1], [0, 1], linestyle="--", color="gray")
            ax.set_xlabel("FPR")
            ax.set_ylabel("TPR")
            ax.set_title("ROC Curve")
            ax.legend(loc="best")
            _save_fig("roc_curve", fig)
    except Exception:
        pass

    # render PR curve
    try:
        if "pr_curve" in result:
            precision = result["pr_curve"]["precision"]
            recall = result["pr_curve"]["recall"]
            fig, ax = plt.subplots()
            ax.plot(recall, precision, label=f"PR (AP={result.get('pr_auc', 'n/a')})")
            ax.set_xlabel("Recall")
            ax.set_ylabel("Precision")
            ax.set_title("Precision-Recall Curve")
            ax.legend(loc="best")
            _save_fig("pr_curve", fig)
    except Exception:
        pass

    # render confusion matrix
    try:
        if "confusion_matrix" in result:
            cm = result["confusion_matrix"]
            fig, ax = plt.subplots()
            im = ax.imshow(cm, cmap="Blues", interpolation="nearest")
            ax.set_title("Confusion Matrix")
            fig.colorbar(im, ax=ax)
            # annotate cells
            for i in range(len(cm)):
                for j in range(len(cm[i])):
                    ax.text(j, i, str(cm[i][j]), ha="center", va="center", color="black")
            ax.set_xlabel("Predicted")
            ax.set_ylabel("Actual")
            _save_fig("confusion_matrix", fig)
    except Exception:
        pass

    # render learning curve
    try:
        if "learning_curve" in result:
            lc = result["learning_curve"]
            fig, ax = plt.subplots()
            ax.plot(lc["train_sizes"], lc["train_scores_mean"], label="Train")
            ax.plot(lc["train_sizes"], lc["test_scores_mean"], label="Test")
            ax.set_xlabel("Training Samples")
            ax.set_ylabel("Score")
            ax.set_title("Learning Curve")
            ax.legend(loc="best")
            _save_fig("learning_curve", fig)
    except Exception:
        pass

    # render feature importance
    try:
        if "feature_importance" in result:
            fi = result["feature_importance"]
            names = [f["name"] for f in fi]
            vals = [f["importance"] for f in fi]
            fig, ax = plt.subplots(figsize=(max(6, len(names)*0.4), 4))
            ax.barh(names, vals)
            ax.set_xlabel("Importance")
            ax.set_title("Feature Importance")
            _save_fig("feature_importance", fig)
    except Exception:
        pass

    # render shap summary (if provided)
    try:
        if "shap_summary" in result:
            ss = result["shap_summary"]
            names = [s["name"] for s in ss]
            vals = [s["mean_abs_shap"] for s in ss]
            fig, ax = plt.subplots(figsize=(max(6, len(names)*0.4), 4))
            ax.barh(names, vals)
            ax.set_xlabel("Mean |SHAP value|")
            ax.set_title("SHAP Summary")
            _save_fig("shap_summary", fig)
    except Exception:
        pass

    result["plots"] = saved_plots
    return result

@router.get("/dashboard/datasets/columns")
def get_columns(
    filename: str = Query(..., description="Name of the dataset file"),
    current_user: User = Depends(get_current_user)
):
    user_folder = os.path.join("uploads", current_user.username)
    file_path = os.path.join(user_folder, filename + "_processed.csv")


    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    try:
        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
        return {"columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")


@router.get("/dashboard/datasets/models")
def fetch_models(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Return all models that the current user has trained on a specific dataset.
    """
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    try:
        # Query all models from the unified Model table
        models = (
            db.query(DefaultModel)
            .filter(DefaultModel.user_id == current_user.id, DefaultModel.dataset == filename)
            .all()
        )

        # Format response: include both model type and ID for clarity
        model_list = [
            f"{m.model_type}_{m.id}" for m in models
        ]

        return {"models": model_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")






@router.get("/dashboard/compare_models")
def compare_models(
    model_ids:  List[int] = Query(), 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """
    Compare two models by their IDs.
    Returns a list of model data suitable for frontend display.
    """
    if len(model_ids) != 2:
        raise HTTPException(status_code=400, detail="Must provide exactly 2 model IDs")

    models_data = []

    for model_id in model_ids:
        model = (
            db.query(DefaultModel)
            .filter(DefaultModel.id == model_id, DefaultModel.user_id == current_user.id)
            .first()
        )
        if not model:
            raise HTTPException(status_code=404, detail=f"Model with ID {model_id} not found for user")

        models_data.append({
            "model_id": model.id,
            "model_type": model.model_type,
            "config": model.parameters,      # dict/json
            "metrics": model.metrics     # dict/json
        })

    return models_data  # <-- return as list instead of dataset1/dataset2



@router.get("/dashboard/plot/{plot_id}")
def get_plot(plot_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plot = db.query(Plot).filter(Plot.id == plot_id).first()
    if not plot:
        raise HTTPException(status_code=404, detail="Plot not found")

    # Optionally: check if plot belongs to current user
    if plot.dataset.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this plot")

    return Response(content=plot.image, media_type="image/png")