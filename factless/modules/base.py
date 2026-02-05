"""
Base module class for FACTLESS analysis pipeline.
"""

import time
from abc import ABC, abstractmethod
from typing import Any, List
from loguru import logger

from ..models import ModuleResult


class BaseModule(ABC):
    """Base class for all FACTLESS analysis modules."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logs: List[str] = []
    
    def log(self, message: str, level: str = "INFO"):
        """Add a log entry for this module."""
        log_entry = f"[{level}] {message}"
        self.logs.append(log_entry)
        
        # Also log to system logger
        if level == "ERROR":
            logger.error(f"{self.module_name}: {message}")
        elif level == "WARNING":
            logger.warning(f"{self.module_name}: {message}")
        else:
            logger.info(f"{self.module_name}: {message}")
    
    def process(self, *args, **kwargs) -> ModuleResult:
        """Process input and return results with timing."""
        start_time = time.time()
        self.logs.clear()
        
        try:
            self.log(f"Starting {self.module_name} processing")
            result = self._process(*args, **kwargs)
            
            processing_time_ms = (time.time() - start_time) * 1000
            self.log(f"Completed in {processing_time_ms:.2f}ms")
            
            # Add timing and logs to result
            result.processing_time_ms = processing_time_ms
            result.logs = self.logs.copy()
            
            return result
            
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            self.log(f"Error during processing: {str(e)}", "ERROR")
            
            # Return error result
            error_result = self._create_error_result(str(e))
            error_result.processing_time_ms = processing_time_ms
            error_result.logs = self.logs.copy()
            
            return error_result
    
    @abstractmethod
    def _process(self, *args, **kwargs) -> ModuleResult:
        """Implement the actual processing logic."""
        pass
    
    @abstractmethod
    def _create_error_result(self, error_message: str) -> ModuleResult:
        """Create an error result for this module type."""
        pass