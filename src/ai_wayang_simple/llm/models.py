"""
Models for structured formatted output
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class WayangOperation(BaseModel):
    cat: str
    id: int
    input: List[int] = Field(default_factory=list)
    output: List[int] = Field(default_factory=list)
    operatorName: str
    keyUdf: Optional[str] = None
    udf: Optional[str] = None
    table: Optional[str] = None
    columnNames: List[str] = Field(default_factory=list)

class WayangPlan(BaseModel):
    operations: List[WayangOperation]
    description_of_plan: str