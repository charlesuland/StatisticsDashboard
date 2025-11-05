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

ALLOWED_EXTENSIONS = {".txt", ".csv", ".xlsx", ".xls"}

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
    user_folder = os.path.join("uploads", str(current_user.username))
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, str(file.filename))

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
        # pandas may require an explicit engine for xlsx (openpyxl). Provide a helpful error if missing.
        try:
            df = pd.read_excel(file.file, engine='openpyxl')
            delimiter = None
        except ValueError:
            raise HTTPException(status_code=400, detail="Failed to read .xlsx file: openpyxl engine required. Ensure 'openpyxl' is installed on the server.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read Excel file: {e}")
    elif ext.lower() == ".xls":
        # older Excel format; try using xlrd if available
        try:
            df = pd.read_excel(file.file, engine='xlrd')
            delimiter = None
        except ValueError:
            raise HTTPException(status_code=400, detail="Failed to read .xls file: xlrd engine required. Ensure 'xlrd' is installed on the server.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read Excel (.xls) file: {e}")

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

    config_folder = os.path.join("configs", str(current_user.username))
    os.makedirs(config_folder, exist_ok=True)
    config_path = os.path.join(config_folder, file.filename + "_config.json")
    with open(config_path, "w") as f:
        json.dump(pipeline_config, f, indent=4)

    # Save processed DataFrame without encoding step
    processed_path = os.path.join(user_folder, str(file.filename) + "_processed.csv")
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
    test_split = float(body.get("test_split"))
    model_name = body.get("model")

    model_params = body.get("params", {})  # hyperparameters
    truth_spec = body.get("truth_spec")

    if not all([filename, target, features, model_name]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Load processed dataset
    file_path = os.path.join("uploads", str(current_user.username), str(filename) + "_processed.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    df = pd.read_csv(file_path)

    # Train the model
    if model_name not in ml.models:
        raise HTTPException(status_code=400, detail=f"Invalid model: {model_name}")
        
    try:
        # Instantiate manager and attach truth_spec if provided
        manager = ml.models[model_name](df, test_split, **model_params)
        if truth_spec:
            # attach to manager for use during prepare_xy/evaluation
            try:
                manager.truth_spec = truth_spec
            except Exception:
                pass
        result = manager.train(target, features)
    except Exception as e:
        return {"success": False, "error": str(e)}

    # Get SQLAlchemy model/table class from mapping
    model_table_class = DefaultModel
    if model_table_class is None:
        raise HTTPException(status_code=400, detail=f"No DB table mapped for model: {model_name}")

    # Save configuration and results to the specific model table
    # include truth_spec in saved parameters for reproducibility
    saved_params = dict(model_params) if isinstance(model_params, dict) else {}
    if truth_spec:
        saved_params['truth_spec'] = truth_spec

    model_entry = model_table_class(
        user_id=current_user.id,
        dataset=filename,
        model_type=model_name,
        parameters=saved_params,
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

    # Instead of rendering and storing server-side PNGs, return structured numeric
    # plot data to the frontend so the client can render plots. Keep `plots` empty
    # for backwards compatibility and add `plot_data` with typed descriptors.
    plot_data = []

    try:
        if "roc_curve" in result:
            rc = result["roc_curve"]
            # rc may be binary {fpr:..., tpr:...} or multiclass {classes: [...], fpr: [...], tpr: [...]}.
            if isinstance(rc, dict) and rc.get('classes') and isinstance(rc.get('fpr'), list):
                plot_data.append({
                    "name": "ROC Curve (per-class)",
                    "key": "roc_curve",
                    "type": "roc",
                    "data": {"classes": rc.get('classes', []), "fpr": rc.get('fpr', []), "tpr": rc.get('tpr', []), "auc": result.get("roc_auc")},
                })
            else:
                plot_data.append({
                    "name": "ROC Curve",
                    "key": "roc_curve",
                    "type": "roc",
                    "data": {"fpr": rc.get("fpr", []), "tpr": rc.get("tpr", []), "auc": result.get("roc_auc")},
                })
    except Exception:
        pass

    try:
        if "pr_curve" in result:
            pr = result["pr_curve"]
            plot_data.append({
                "name": "Precision-Recall Curve",
                "key": "pr_curve",
                "type": "pr",
                "data": {"precision": pr.get("precision", []), "recall": pr.get("recall", []), "ap": result.get("pr_auc")},
            })
    except Exception:
        pass

    try:
        if "confusion_matrix" in result:
            cm = result["confusion_matrix"]
            # Ensure it's a list of lists (JSON serializable)
            plot_data.append({
                "name": "Confusion Matrix",
                "key": "confusion_matrix",
                "type": "confusion_matrix",
                "data": {"matrix": cm},
            })
    except Exception:
        pass

    try:
        if "learning_curve" in result:
            lc = result["learning_curve"]
            plot_data.append({
                "name": "Learning Curve",
                "key": "learning_curve",
                "type": "learning_curve",
                "data": {
                    "train_sizes": lc.get("train_sizes", []),
                    "train_scores_mean": lc.get("train_scores_mean", []),
                    "test_scores_mean": lc.get("test_scores_mean", []),
                },
            })
    except Exception:
        pass

    try:
        if "feature_importance" in result:
            fi = result["feature_importance"]
            plot_data.append({
                "name": "Feature Importance",
                "key": "feature_importance",
                "type": "feature_importance",
                "data": fi,
            })
    except Exception:
        pass

    try:
        if "shap_summary" in result:
            ss = result["shap_summary"]
            plot_data.append({
                "name": "SHAP Summary",
                "key": "shap_summary",
                "type": "shap_summary",
                "data": ss,
            })
    except Exception:
        pass

    # Keep `plots` empty for compatibility with older frontends that expect image ids.
    saved_plots = []
    try:
        for pd_item in plot_data:
            plot = Plot(user_id=current_user.id, dataset_id=dataset.id, name=pd_item.get("key") or pd_item.get("name"), data=pd_item, image=None)
            db.add(plot)
            db.commit()
            db.refresh(plot)
            saved_plots.append({"id": plot.id, "name": plot.name})
    except Exception as e:
        # If saving fails, continue but leave saved_plots as-is
        print("Warning: failed to save plots to DB:", e)

    result["plots"] = saved_plots
    result["plot_data"] = plot_data
    return result

@router.get("/dashboard/datasets/columns")
def get_columns(
    filename: str = Query(..., description="Name of the dataset file"),
    current_user: User = Depends(get_current_user)
):
    user_folder = os.path.join("uploads", str(current_user.username))
    file_path = os.path.join(user_folder, filename + "_processed.csv")


    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    try:
        df = pd.read_csv(file_path)
        columns = df.columns.tolist()
        return {"columns": columns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")


@router.get("/dashboard/datasets/column_info")
def get_column_info(
    filename: str = Query(..., description="Name of the dataset file"),
    current_user: User = Depends(get_current_user),
):
    """
    Return column dtype information from the stored preprocessing config if available.
    Falls back to empty mapping when no config exists.
    """
    config_path = os.path.join("configs", current_user.username, filename + "_config.json")
    if not os.path.exists(config_path):
        return {"dtypes": {}}
    try:
        with open(config_path, "r") as f:
            cfg = json.load(f)
        return {"dtypes": cfg.get("dtypes", {})}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read config: {e}")



@router.get("/dashboard/datasets/info")
def dataset_info(
    filename: str = Query(..., description="Name of the dataset file"),
    current_user: User = Depends(get_current_user),
):
    """
    Return simple dataset information: row count and missing values (from config if available).
    """
    user_folder = os.path.join("uploads", str(current_user.username))
    file_path = os.path.join(user_folder, filename + "_processed.csv")
    config_path = os.path.join("configs", str(current_user.username), filename + "_config.json")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    try:
        df = pd.read_csv(file_path)
        row_count = int(df.shape[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")

    missing_values = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                cfg = json.load(f)
            missing_values = cfg.get('missing_values', {})
        except Exception:
            missing_values = {}

    return {"row_count": row_count, "missing_values": missing_values}


@router.get('/dashboard/datasets/preview')
def dataset_preview(
    filename: str = Query(..., description="Name of the dataset file"),
    n: int = Query(10, description="Number of rows to preview"),
    current_user: User = Depends(get_current_user),
):
    user_folder = os.path.join('uploads', str(current_user.username))
    file_path = os.path.join(user_folder, filename + '_processed.csv')
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail='File not found')
    try:
        df = pd.read_csv(file_path)
        rows = df.head(n).to_dict(orient='records')
        return {'rows': rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to read CSV: {e}')


@router.get('/dashboard/datasets/download')
def dataset_download(
    filename: str = Query(..., description='Name of the dataset file'),
    current_user: User = Depends(get_current_user)
):
    user_folder = os.path.join('uploads', str(current_user.username))
    file_path = os.path.join(user_folder, filename + '_processed.csv')
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail='File not found')
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return Response(content, media_type='text/csv')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to read file: {e}')


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
            "model_type": model.model_type,      # e.g., "linear_regression", "decision_tree"
            # training_time may not exist on older records, so use getattr with default
            "training_time": getattr(model, "training_time", None),
            # use stored parameters and metrics columns
            "config": model.parameters,
            "metrics": model.metrics,
        })

    return models_data  # <-- return as list instead of dataset1/dataset2


@router.get("/dashboard/models/{model_name}")
def get_model(
    model_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Return a single model record by id for the current user.
    """
    # Extract model ID from model_name
    try:
        model_id = int(model_name.split("_")[-1])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid model name format")

    model = (
        db.query(DefaultModel)
        .filter(DefaultModel.id == model_id, DefaultModel.user_id == current_user.id)
        .first()
    )
    if not model:
        raise HTTPException(status_code=404, detail=f"Model with ID {model_id} not found for user")

    return {
        "model_id": model.id,
        "model_type": model.model_type,
        "training_time": getattr(model, "training_time", None),
        "parameters": model.parameters,
        "metrics": model.metrics,
        "created_at": model.created_at.isoformat() if getattr(model, 'created_at', None) else None,
    }



@router.get('/dashboard/models')
def list_models_grouped(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Return all models for the current user grouped by dataset.
    Response format: { "dataset1.csv": [ { "id": 1, "model_type": "decision_tree", "created_at": "..." }, ... ], ... }
    """
    try:
        models = db.query(DefaultModel).filter(DefaultModel.user_id == current_user.id).order_by(DefaultModel.dataset, DefaultModel.created_at.desc()).all()
        grouped = {}
        for m in models:
            key = m.dataset or 'unknown'
            entry = { 'id': m.id, 'model_type': m.model_type, 'created_at': m.created_at.isoformat() if getattr(m, 'created_at', None) else None }
            grouped.setdefault(key, []).append(entry)
        return grouped
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error fetching models: {e}')
