from src.schema import TaskRecord
from src.evidence.evidence_builder import EvidenceRecord

def rollup_phase(tasks: list[TaskRecord], evidences: list[EvidenceRecord]) -> str:
    # Worst-of logic
    statuses = [e.status for e in evidences if e.status != "Not Scored"]
    if "Red" in statuses:
        return "Red"
    if "Amber" in statuses:
        return "Amber"
    return "Green"

def rollup_project(phase_statuses: dict[str, str], all_tasks: list[TaskRecord], cfg: dict) -> tuple[str, bool]:
    base_status = "Green"
    if "Red" in phase_statuses.values():
        base_status = "Red"
    elif "Amber" in phase_statuses.values():
        base_status = "Amber"
        
    cfg_rollup = cfg.get("rollup", {})
    override_pct = cfg_rollup.get("project_overdue_pct_override", 0.30)
    
    # Calculate % overdue open tasks
    open_tasks = [t for t in all_tasks if t.status != "Completed" and t.status != "Not Applicable"]
    if not open_tasks:
        return base_status, False
        
    overdue_count = len([t for t in open_tasks if (t.variance_days is not None and t.variance_days < 0)])
    
    pct_overdue = overdue_count / len(open_tasks)
    
    override_triggered = False
    if pct_overdue > override_pct:
        if base_status != "Red":
            base_status = "Red"
            override_triggered = True
            
    return base_status, override_triggered
