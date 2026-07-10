from pydantic import BaseModel
from datetime import date
from typing import Optional, Literal

Confidence = Literal["direct", "inferred", "computed", "assumed", "missing"]

class TaskRecord(BaseModel):
    task_id: str                     # stable synthetic id: f"{project_id}_{row_index}"
    task_name: Optional[str]
    phase_milestone: Optional[str]
    level: Optional[int] = None      # None if source has no Level column
    ancestors: Optional[str] = None
    status: Optional[str] = None     # raw string: Not Started / In Progress / Completed / On Hold
    pct_complete: Optional[float] = None
    baseline_start: Optional[date] = None
    baseline_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    variance_days: Optional[int] = None
    total_float: Optional[int] = None
    is_critical_path: bool = False
    on_hold: bool = False
    not_applicable: bool = False
    priority: Optional[str] = None
    status_comment: Optional[str] = None
    field_confidence: dict[str, Confidence] = {}

class CommentRecord(BaseModel):
    linked_row_ref: Optional[str]    # e.g. "Row 292"
    author: Optional[str]
    timestamp: Optional[str]
    text: str

class ProjectSummary(BaseModel):
    project_name: str
    project_manager: Optional[str] = None
    project_start: Optional[date] = None
    project_end: Optional[date] = None
    pct_complete: Optional[float] = None
    project_stage: Optional[str] = None
    at_risk_flag: Optional[str] = None
    source_schedule_health: Optional[str] = None

class ProjectPlan(BaseModel):
    project_id: str
    source_file: str
    source_format: Literal["xlsx", "docx", "pdf"]
    summary: ProjectSummary
    tasks: list[TaskRecord]
    comments: list[CommentRecord]
    parse_warnings: list[str] = []
