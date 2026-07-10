from pydantic import BaseModel
from typing import Literal, Optional

Confidence = Literal["direct", "inferred", "computed", "assumed", "missing"]

class EvidenceRecord(BaseModel):
    signal: str
    status: Literal["Green", "Amber", "Red", "Not Scored"]
    trigger_type: Optional[str]
    supporting_facts: list[str]
    confidence: Confidence
