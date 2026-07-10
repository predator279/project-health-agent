from datetime import date
from src.schema import TaskRecord, CommentRecord
from src.evidence.evidence_builder import EvidenceRecord

def score_schedule_slippage(task: TaskRecord, cfg: dict, today: date) -> EvidenceRecord:
    if task.status in ["Completed", "Not Applicable"]:
        return EvidenceRecord(
            signal="schedule_slippage",
            status="Green",
            trigger_type="completed",
            supporting_facts=[f"Task '{task.task_name}' is {task.status}."],
            confidence="direct"
        )
        
    variance = task.variance_days if task.variance_days is not None else 0
    
    # Check overdue against actual baseline if available and past
    overdue_days = 0
    if task.baseline_end and task.baseline_end < today and task.status != "Completed":
        overdue_days = (today - task.baseline_end).days
        
    # Use variance if overdue isn't strictly positive based on today
    if overdue_days <= 0 and variance < 0:
        overdue_days = abs(variance)
        
    cfg_slip = cfg.get("schedule_slippage", {})
    amber_min = cfg_slip.get("amber_overdue_days_min", 1)
    red_min = cfg_slip.get("red_overdue_days", 10)
    
    if overdue_days >= red_min:
        return EvidenceRecord(
            signal="schedule_slippage",
            status="Red",
            trigger_type="critical_delay",
            supporting_facts=[f"Task '{task.task_name}' is delayed by {overdue_days} days."],
            confidence="computed"
        )
    elif overdue_days >= amber_min:
        return EvidenceRecord(
            signal="schedule_slippage",
            status="Amber",
            trigger_type="warning_delay",
            supporting_facts=[f"Task '{task.task_name}' is delayed by {overdue_days} days."],
            confidence="computed"
        )
        
    return EvidenceRecord(
        signal="schedule_slippage",
        status="Green",
        trigger_type="on_track",
        supporting_facts=[f"Task '{task.task_name}' is on schedule."],
        confidence="computed"
    )

def score_milestone_health(phase_tasks: list[TaskRecord], cfg: dict, today: date) -> EvidenceRecord:
    # A simple phase drift calculation based on % incomplete past due date
    pts_behind = 0
    cfg_milestone = cfg.get("milestone_health", {})
    amber_min = cfg_milestone.get("amber_pts_behind_min", 5)
    red_min = cfg_milestone.get("red_pts_behind", 15)
    
    for t in phase_tasks:
        if t.status != "Completed" and t.baseline_end and t.baseline_end < today:
            # Add 1 point for every day late, capped at 20 per task
            days_late = (today - t.baseline_end).days
            pts_behind += min(days_late, 20)
            
    if pts_behind >= red_min:
        return EvidenceRecord(
            signal="milestone_health",
            status="Red",
            trigger_type="phase_drift",
            supporting_facts=[f"Phase has accumulated {pts_behind} drift points across delayed tasks."],
            confidence="computed"
        )
    elif pts_behind >= amber_min:
        return EvidenceRecord(
            signal="milestone_health",
            status="Amber",
            trigger_type="phase_drift_warning",
            supporting_facts=[f"Phase has accumulated {pts_behind} drift points."],
            confidence="computed"
        )
        
    return EvidenceRecord(
        signal="milestone_health",
        status="Green",
        trigger_type="on_track",
        supporting_facts=["Phase milestones are generally on track."],
        confidence="computed"
    )

def score_blockers(task: TaskRecord, comments: list[CommentRecord], cfg: dict, history: list[dict] | None) -> EvidenceRecord:
    cfg_blockers = cfg.get("blockers", {})
    keywords = cfg_blockers.get("keywords", [])
    
    task_comments = [c for c in comments if c.linked_row_ref == task.task_id]
    text_to_search = (task.status_comment or "") + " " + " ".join([c.text for c in task_comments])
    text_to_search = text_to_search.lower()
    
    found_keywords = [kw for kw in keywords if kw.lower() in text_to_search]
    
    if found_keywords:
        return EvidenceRecord(
            signal="blockers",
            status="Amber",
            trigger_type="keyword_match",
            supporting_facts=[f"Task '{task.task_name}' has blocker keywords: {', '.join(found_keywords)}."],
            confidence="inferred"
        )
        
    return EvidenceRecord(
        signal="blockers",
        status="Green",
        trigger_type="no_blockers",
        supporting_facts=[f"No explicit blockers found for '{task.task_name}'."],
        confidence="computed"
    )

def score_budget_burn(task: TaskRecord, cfg: dict) -> EvidenceRecord | None:
    # Extended signal: if no cost fields (we don't have them in schema), return None
    return None
