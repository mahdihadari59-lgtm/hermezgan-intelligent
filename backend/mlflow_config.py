"""MLflow Tracking Server Configuration for HDP AI Model Registry

Provides centralized model tracking, versioning, and serving capabilities.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import mlflow
import mlflow.sklearn
import mlflow.pytorch
import mlflow.tensorflow
from mlflow.tracking import MlflowClient
from mlflow.entities import ViewType

logger = logging.getLogger(__name__)


class MLflowConfig:
    """MLflow Configuration Manager"""
    
    def __init__(self):
        self.tracking_uri = os.getenv(
            "MLFLOW_TRACKING_URI",
            "http://localhost:5000"
        )
        self.backend_store_uri = os.getenv(
            "MLFLOW_BACKEND_STORE_URI",
            "sqlite:///mlflow/mlflow.db"
        )
        self.default_artifact_root = os.getenv(
            "MLFLOW_ARTIFACT_ROOT",
            "./mlflow/artifacts"
        )
        self.registry_uri = os.getenv(
            "MLFLOW_REGISTRY_URI",
            self.backend_store_uri
        )
        
        # Initialize MLflow
        self._setup_tracking()
    
    def _setup_tracking(self):
        """Configure MLflow tracking backend"""
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_registry_uri(self.registry_uri)
            logger.info(f"✅ MLflow configured: {self.tracking_uri}")
        except Exception as e:
            logger.error(f"❌ MLflow setup failed: {e}")
            raise
    
    def start_run(self, experiment_name: str, run_name: str = None) -> str:
        """Start a new MLflow run"""
        try:
            mlflow.set_experiment(experiment_name)
            run = mlflow.start_run(run_name=run_name)
            logger.info(f"✅ MLflow run started: {run.info.run_id}")
            return run.info.run_id
        except Exception as e:
            logger.error(f"❌ Failed to start run: {e}")
            raise
    
    def log_params(self, params: Dict[str, Any]):
        """Log hyperparameters"""
        try:
            for key, value in params.items():
                mlflow.log_param(key, value)
            logger.info(f"✅ Logged {len(params)} parameters")
        except Exception as e:
            logger.error(f"❌ Failed to log params: {e}")
    
    def log_metrics(self, metrics: Dict[str, float], step: int = None):
        """Log metrics"""
        try:
            for key, value in metrics.items():
                mlflow.log_metric(key, value, step=step)
            logger.info(f"✅ Logged {len(metrics)} metrics")
        except Exception as e:
            logger.error(f"❌ Failed to log metrics: {e}")
    
    def log_model(self, model, artifact_path: str, framework: str = "sklearn"):
        """Log model to registry"""
        try:
            if framework == "sklearn":
                mlflow.sklearn.log_model(model, artifact_path)
            elif framework == "pytorch":
                mlflow.pytorch.log_model(model, artifact_path)
            elif framework == "tensorflow":
                mlflow.tensorflow.log_model(model, artifact_path)
            else:
                raise ValueError(f"Unsupported framework: {framework}")
            logger.info(f"✅ Model logged: {artifact_path}")
        except Exception as e:
            logger.error(f"❌ Failed to log model: {e}")
            raise
    
    def register_model(self, model_uri: str, name: str, description: str = None):
        """Register model in registry"""
        try:
            client = MlflowClient(self.tracking_uri)
            result = mlflow.register_model(model_uri, name)
            
            if description:
                client.update_registered_model(
                    name=name,
                    description=description
                )
            
            logger.info(f"✅ Model registered: {name}")
            return result
        except Exception as e:
            logger.error(f"❌ Failed to register model: {e}")
            raise
    
    def end_run(self, status: str = "FINISHED"):
        """End current MLflow run"""
        try:
            mlflow.end_run(status=status)
            logger.info(f"✅ MLflow run ended: {status}")
        except Exception as e:
            logger.error(f"❌ Failed to end run: {e}")
    
    def get_model_version(self, name: str, version: int = None, stage: str = None):
        """Get model from registry"""
        try:
            client = MlflowClient(self.tracking_uri)
            
            if stage:
                model = client.get_latest_versions(name, stages=[stage])[0]
            elif version:
                model = client.get_model_version(name, version)
            else:
                versions = client.get_latest_versions(name)
                model = versions[0] if versions else None
            
            return model
        except Exception as e:
            logger.error(f"❌ Failed to get model: {e}")
            return None
    
    def transition_model_stage(
        self,
        name: str,
        version: int,
        stage: str,
        archive_existing_versions: bool = True
    ):
        """Transition model to new stage (Staging/Production)"""
        try:
            client = MlflowClient(self.tracking_uri)
            client.transition_model_version_stage(
                name=name,
                version=version,
                stage=stage,
                archive_existing_versions=archive_existing_versions
            )
            logger.info(f"✅ Model {name} v{version} transitioned to {stage}")
        except Exception as e:
            logger.error(f"❌ Failed to transition model: {e}")
    
    def list_experiments(self):
        """List all experiments"""
        try:
            client = MlflowClient(self.tracking_uri)
            experiments = client.search_experiments()
            return experiments
        except Exception as e:
            logger.error(f"❌ Failed to list experiments: {e}")
            return []
    
    def search_runs(self, experiment_ids: list, max_results: int = 100):
        """Search runs by experiment"""
        try:
            client = MlflowClient(self.tracking_uri)
            runs = client.search_runs(
                experiment_ids=experiment_ids,
                max_results=max_results
            )
            return runs
        except Exception as e:
            logger.error(f"❌ Failed to search runs: {e}")
            return []


# Global instance
_mlflow_config = None


def get_mlflow_config() -> MLflowConfig:
    """Get or create MLflow config instance"""
    global _mlflow_config
    if _mlflow_config is None:
        _mlflow_config = MLflowConfig()
    return _mlflow_config
