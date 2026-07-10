from pydantic import BaseModel
from typing import Optional

class Trend(BaseModel):
    category: str
    signal: str
    affected_project_ids: list[str]
    example_facts: list[str]

def detect_trends(project_reports: list[dict], cfg: dict) -> list[Trend]:
    """
    Detects cross-project trends.
    A trend is defined here as a signal (e.g. Schedule Slippage) that appears as 
    Amber or Red in >= 2 projects.
    """
    trends = []
    
    # We only have 2 projects, so if both have the same issue, it's a trend.
    signal_counts = {}
    signal_facts = {}
    
    for report in project_reports:
        project_id = report.get("project_id", "Unknown")
        for ev in report.get("evidences", []):
            if ev.get("status") in ["Red", "Amber"]:
                sig = ev.get("signal")
                
                if sig not in signal_counts:
                    signal_counts[sig] = []
                    signal_facts[sig] = []
                    
                signal_counts[sig].append(project_id)
                # Just take the first supporting fact as an example
                if ev.get("supporting_facts"):
                    signal_facts[sig].append(f"[{project_id}] {ev['supporting_facts'][0]}")
                    
    for sig, proj_ids in signal_counts.items():
        unique_projs = list(set(proj_ids))
        if len(unique_projs) >= 2:
            trends.append(Trend(
                category="Systemic Delay" if "slippage" in sig else "Execution Risk",
                signal=sig,
                affected_project_ids=unique_projs,
                example_facts=signal_facts[sig][:3]  # cap at 3 facts
            ))
            
    return trends
