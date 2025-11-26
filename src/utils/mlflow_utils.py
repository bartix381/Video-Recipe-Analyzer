"""MLflow utilities for experiment tracking."""
import mlflow
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MLflowTracker:
    """MLflow experiment tracking wrapper."""
    
    def __init__(self, experiment_name: str, tracking_uri: Optional[str] = None):
        """
        Initialize MLflow tracker.
        
        Args:
            experiment_name: Name of the experiment
            tracking_uri: MLflow tracking URI (directory path or server URL)
        """
        self.experiment_name = experiment_name
        
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
            logger.info(f"Set MLflow tracking URI: {tracking_uri}")
        
        # Create or get experiment
        try:
            self.experiment_id = mlflow.create_experiment(experiment_name)
            logger.info(f"Created new experiment: {experiment_name}")
        except:
            experiment = mlflow.get_experiment_by_name(experiment_name)
            self.experiment_id = experiment.experiment_id
            logger.info(f"Using existing experiment: {experiment_name}")
        
        mlflow.set_experiment(experiment_name)
        self.run = None
    
    def start_run(self, run_name: Optional[str] = None) -> str:
        """
        Start a new MLflow run.
        
        Args:
            run_name: Name for the run
            
        Returns:
            Run ID
        """
        if run_name is None:
            run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.run = mlflow.start_run(run_name=run_name)
        logger.info(f"Started MLflow run: {run_name} (ID: {self.run.info.run_id})")
        return self.run.info.run_id
    
    def log_params(self, params: Dict[str, Any]):
        """Log parameters to MLflow."""
        for key, value in params.items():
            mlflow.log_param(key, value)
        logger.debug(f"Logged {len(params)} parameters")
    
    def log_param(self, key: str, value: Any):
        """Log a single parameter."""
        mlflow.log_param(key, value)
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """
        Log metrics to MLflow.
        
        Args:
            metrics: Dictionary of metric names and values
            step: Optional step number
        """
        for key, value in metrics.items():
            mlflow.log_metric(key, value, step=step)
        logger.debug(f"Logged {len(metrics)} metrics")
    
    def log_metric(self, key: str, value: float, step: Optional[int] = None):
        """Log a single metric."""
        mlflow.log_metric(key, value, step=step)
    
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """
        Log an artifact (file) to MLflow.
        
        Args:
            local_path: Local file path
            artifact_path: Artifact subdirectory
        """
        mlflow.log_artifact(local_path, artifact_path)
        logger.debug(f"Logged artifact: {local_path}")
    
    def log_artifacts(self, local_dir: str, artifact_path: Optional[str] = None):
        """
        Log all files in a directory as artifacts.
        
        Args:
            local_dir: Local directory path
            artifact_path: Artifact subdirectory
        """
        mlflow.log_artifacts(local_dir, artifact_path)
        logger.debug(f"Logged artifacts from: {local_dir}")
    
    def log_dict(self, dictionary: Dict, filename: str):
        """
        Log a dictionary as a JSON artifact.
        
        Args:
            dictionary: Dictionary to log
            filename: Artifact filename
        """
        mlflow.log_dict(dictionary, filename)
        logger.debug(f"Logged dictionary as: {filename}")
    
    def log_text(self, text: str, filename: str):
        """
        Log text as an artifact.
        
        Args:
            text: Text content
            filename: Artifact filename
        """
        mlflow.log_text(text, filename)
        logger.debug(f"Logged text as: {filename}")
    
    def set_tag(self, key: str, value: Any):
        """Set a tag for the run."""
        mlflow.set_tag(key, value)
    
    def set_tags(self, tags: Dict[str, Any]):
        """Set multiple tags."""
        mlflow.set_tags(tags)
    
    def end_run(self):
        """End the current MLflow run."""
        if self.run:
            mlflow.end_run()
            logger.info(f"Ended MLflow run: {self.run.info.run_id}")
            self.run = None
    
    def __enter__(self):
        """Context manager entry."""
        self.start_run()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.end_run()


def setup_mlflow(config: Dict[str, Any]) -> MLflowTracker:
    """
    Setup MLflow tracking from configuration.
    
    Args:
        config: Configuration dictionary with mlflow section
        
    Returns:
        MLflowTracker instance
    """
    mlflow_config = config.get('mlflow', {})
    experiment_name = mlflow_config.get('experiment_name', 'recipe-video-extraction')
    tracking_uri = mlflow_config.get('tracking_uri', './experiments/mlruns')
    
    return MLflowTracker(experiment_name, tracking_uri)
