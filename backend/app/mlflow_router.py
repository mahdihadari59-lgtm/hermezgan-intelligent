"""MLflow Model Registry API Endpoints

Provides REST endpoints for model tracking, registration, and serving.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import logging

from ..mlflow_config import get_mlflow_config

logger = logging.getLogger(__name__)
router = APIRouter()


class ExperimentCreate(BaseModel):
    """Create experiment request"""
    name: str
    tags: Optional[dict] = None


class RunCreate(BaseModel):
    """Start run request"""
    experiment_name: str
    run_name: Optional[str] = None
    tags: Optional[dict] = None


class MetricsLog(BaseModel):
    """Log metrics request"""
    run_id: str
    metrics: dict
    step: Optional[int] = None


class ParamsLog(BaseModel):
    """Log parameters request"""
    run_id: str
    params: dict


class ModelRegister(BaseModel):
    """Register model request"""
    model_uri: str
    name: str
    description: Optional[str] = None


class ModelTransition(BaseModel):
    """Transition model request"""
    name: str
    version: int
    stage: str  # Staging, Production, Archived


@router.get("/mlflow/health")
async def mlflow_health():
    """Check MLflow server health"""
    try:
        config = get_mlflow_config()
        experiments = config.list_experiments()
        return {
            "status": "healthy",
            "tracking_uri": config.tracking_uri,
            "experiments_count": len(experiments)
        }
    except Exception as e:
        logger.error(f"MLflow health check failed: {e}")
        raise HTTPException(status_code=503, detail="MLflow server unavailable")


@router.get("/mlflow/experiments")
async def list_experiments():
    """List all MLflow experiments"""
    try:
        config = get_mlflow_config()
        experiments = config.list_experiments()
        return {
            "success": True,
            "experiments": [
                {
                    "id": exp.experiment_id,
                    "name": exp.name,
                    "artifact_location": exp.artifact_location,
                    "lifecycle_stage": exp.lifecycle_stage
                }
                for exp in experiments
            ]
        }
    except Exception as e:
        logger.error(f"Failed to list experiments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mlflow/runs")
async def start_run(run_create: RunCreate):
    """Start a new MLflow run"""
    try:
        config = get_mlflow_config()
        run_id = config.start_run(
            experiment_name=run_create.experiment_name,
            run_name=run_create.run_name
        )
        return {
            "success": True,
            "run_id": run_id,
            "experiment_name": run_create.experiment_name
        }
    except Exception as e:
        logger.error(f"Failed to start run: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mlflow/metrics")
async def log_metrics(metrics_log: MetricsLog):
    """Log metrics to run"""
    try:
        config = get_mlflow_config()
        config.log_metrics(metrics_log.metrics, step=metrics_log.step)
        return {
            "success": True,
            "metrics_count": len(metrics_log.metrics)
        }
    except Exception as e:
        logger.error(f"Failed to log metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mlflow/params")
async def log_params(params_log: ParamsLog):
    """Log parameters to run"""
    try:
        config = get_mlflow_config()
        config.log_params(params_log.params)
        return {
            "success": True,
            "params_count": len(params_log.params)
        }
    except Exception as e:
        logger.error(f"Failed to log params: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mlflow/models/register")
async def register_model(model_reg: ModelRegister):
    """Register model in MLflow registry"""
    try:
        config = get_mlflow_config()
        result = config.register_model(
            model_uri=model_reg.model_uri,
            name=model_reg.name,
            description=model_reg.description
        )
        return {
            "success": True,
            "model_name": model_reg.name,
            "model_uri": str(result)
        }
    except Exception as e:
        logger.error(f"Failed to register model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mlflow/models/transition")
async def transition_model(transition: ModelTransition):
    """Transition model to new stage"""
    try:
        config = get_mlflow_config()
        config.transition_model_stage(
            name=transition.name,
            version=transition.version,
            stage=transition.stage
        )
        return {
            "success": True,
            "model_name": transition.name,
            "version": transition.version,
            "stage": transition.stage
        }
    except Exception as e:
        logger.error(f"Failed to transition model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mlflow/models/{model_name}")
async def get_model(model_name: str, stage: Optional[str] = Query(None)):
    """Get model from registry"""
    try:
        config = get_mlflow_config()
        model = config.get_model_version(model_name, stage=stage)
        
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        
        return {
            "success": True,
            "name": model.name,
            "version": model.version,
            "stage": model.current_stage,
            "source": model.source,
            "status": model.status,
            "created_timestamp": model.creation_timestamp,
            "updated_timestamp": model.last_updated_timestamp
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model: {e}")
        raise HTTPException(status_code=500, detail=str(e))
