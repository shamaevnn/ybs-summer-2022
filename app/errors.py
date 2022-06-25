from fastapi import HTTPException


class BaseError(Exception):
    status_code: int
    description: str

    def __init__(self, status_code: int, description: str) -> None:
        self.status_code = status_code
        self.description = description


class NodeNotFound(HTTPException):
    status_code: int = 404

    def __init__(self, node_id: str) -> None:
        self.detail = f"Node with id={node_id} not found"


class InvalidUUID(HTTPException):
    status_code: int = 400

    def __init__(self, uuid: str) -> None:
        self.detail = f"Current {uuid=} is not valid"
