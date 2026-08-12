# app/schemas/common.py

from typing import Annotated

from bson import ObjectId
from pydantic import BeforeValidator


def validate_object_id(v):
    """
    Accepts a real ObjectId (coming back from Mongo) or a valid
    ObjectId-shaped string (coming in from a URL param) — rejects
    anything else before it reaches business logic.
    """
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str) and ObjectId.is_valid(v):
        return v
    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]