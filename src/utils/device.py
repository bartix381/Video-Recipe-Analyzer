"""Device detection utilities for PyTorch models."""
import torch
import logging
from typing import Literal

logger = logging.getLogger(__name__)

DeviceType = Literal["cpu", "cuda", "mps"]


def get_device(preferred: str = "auto") -> torch.device:
    """
    Detect and return the best available PyTorch device.
    
    Args:
        preferred: Device preference ("auto", "cpu", "cuda", "mps")
        
    Returns:
        torch.device: The selected device
        
    Raises:
        ValueError: If preferred device is not available
    """
    if preferred == "auto":
        if torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            device = torch.device("mps")
            logger.info("Using Apple Metal (MPS) device")
        else:
            device = torch.device("cpu")
            logger.info("Using CPU device")
        return device
    
    elif preferred == "cuda":
        if not torch.cuda.is_available():
            raise ValueError("CUDA requested but not available")
        device = torch.device("cuda")
        logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
        return device
    
    elif preferred == "mps":
        if not torch.backends.mps.is_available():
            raise ValueError("MPS requested but not available")
        device = torch.device("mps")
        logger.info("Using Apple Metal (MPS) device")
        return device
    
    elif preferred == "cpu":
        device = torch.device("cpu")
        logger.info("Using CPU device")
        return device
    
    else:
        raise ValueError(f"Invalid device preference: {preferred}")


def get_device_info() -> dict:
    """
    Get detailed information about available devices.
    
    Returns:
        dict: Device information
    """
    info = {
        "cpu": True,
        "cuda": torch.cuda.is_available(),
        "mps": torch.backends.mps.is_available(),
        "cuda_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
    }
    
    if info["cuda"]:
        info["cuda_devices"] = [
            torch.cuda.get_device_name(i) 
            for i in range(torch.cuda.device_count())
        ]
    
    return info


def supports_fp16(device: torch.device) -> bool:
    """
    Check if device supports FP16 inference.
    
    Args:
        device: PyTorch device
        
    Returns:
        bool: True if FP16 is supported
    """
    if device.type == "cuda":
        return True
    elif device.type == "mps":
        return True  # Apple Metal supports FP16
    else:
        return False
