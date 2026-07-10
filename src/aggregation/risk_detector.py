from pydantic import BaseModel
from typing import Optional

class Risk(BaseModel):
    project_id: str
    risk_description: str
    trajectory: str

def detect_emerging_risks(project_reports: list[dict], history: list[dict] | None) -> list[Risk]:
    """
    Detects emerging risks. Since we only have a single snapshot (no longitudinal data),
    we flag projects with "Red" or "Amber" statuses but report trajectory as "insufficient history".
    """
    risks = []
    
    for report in project_reports:
        status = report.get("status", "Green")
        project_id = report.get("project_id", "Unknown")
        
        if status in ["Red", "Amber"]:
            risks.append(Risk(
                project_id=project_id,
                risk_description=f"Project is currently {status}. Review primary drivers.",
                trajectory="insufficient history to assess trajectory"
            ))
            
    return risks
