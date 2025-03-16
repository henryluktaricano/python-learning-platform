"""
Type stubs for FastAPI
"""
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

class FastAPI:
    """
    FastAPI class for creating web applications
    """
    def __init__(
        self,
        *,
        debug: bool = False,
        title: str = "FastAPI",
        description: str = "",
        version: str = "0.1.0",
        **kwargs: Any,
    ) -> None:
        ...
    
    def include_router(
        self,
        router: Any,
        *,
        prefix: str = "",
        tags: List[str] = None,
        **kwargs: Any,
    ) -> None:
        ...
    
    def add_middleware(
        self,
        middleware_class: Type[Any],
        **kwargs: Any,
    ) -> None:
        ...
    
    def get(
        self,
        path: str,
        *,
        response_model: Any = None,
        status_code: int = 200,
        tags: List[str] = None,
        **kwargs: Any,
    ) -> Callable:
        ...
    
    def post(
        self,
        path: str,
        *,
        response_model: Any = None,
        status_code: int = 200,
        tags: List[str] = None,
        **kwargs: Any,
    ) -> Callable:
        ...
    
    def put(
        self,
        path: str,
        *,
        response_model: Any = None,
        status_code: int = 200,
        tags: List[str] = None,
        **kwargs: Any,
    ) -> Callable:
        ...
    
    def delete(
        self,
        path: str,
        *,
        response_model: Any = None,
        status_code: int = 200,
        tags: List[str] = None,
        **kwargs: Any,
    ) -> Callable:
        ...

class APIRouter:
    """
    APIRouter class for creating modular routes
    """
    def __init__(
        self,
        *,
        prefix: str = "",
        tags: List[str] = None,
        **kwargs: Any,
    ) -> None:
        ...
    
    def include_router(
        self,
        router: Any,
        *,
        prefix: str = "",
        tags: List[str] = None,
        **kwargs: Any,
    ) -> None:
        ...
    
    def get(
        self,
        path: str,
        *,
        response_model: Any = None,
        status_code: int = 200,
        tags: List[str] = None,
        **kwargs: Any,
    ) -> Callable:
        ...
    
    def post(
        self,
        path: str,
        *,
        response_model: Any = None,
        status_code: int = 200,
        tags: List[str] = None,
        **kwargs: Any,
    ) -> Callable:
        ...
    
    def put(
        self,
        path: str,
        *,
        response_model: Any = None,
        status_code: int = 200,
        tags: List[str] = None,
        **kwargs: Any,
    ) -> Callable:
        ...
    
    def delete(
        self,
        path: str,
        *,
        response_model: Any = None,
        status_code: int = 200,
        tags: List[str] = None,
        **kwargs: Any,
    ) -> Callable:
        ...

def Depends(dependency: Callable = None) -> Any:
    """
    Dependency injection function
    """
    ...

class HTTPException(Exception):
    """
    HTTP exception class
    """
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Dict[str, Any] = None,
    ) -> None:
        ...

class Request:
    """
    Request class
    """
    ...

class Response:
    """
    Response class
    """
    ...

__version__ = "0.104.1" 