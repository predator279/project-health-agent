from src.evidence.evidence_builder import EvidenceRecord

def compose_narrative(project_status: str, evidences: list[EvidenceRecord], override_triggered: bool, data_confidence: str) -> str:
    lines = []
    
    # 1. One-line verdict
    top_driver = "Unknown"
    for e in evidences:
        if e.status == project_status:
            top_driver = e.signal.replace("_", " ").title()
            break
            
    lines.append(f"**Overall Status**: {project_status} (Driven by: {top_driver})")
    lines.append("")
    
    # 2. Bulleted contributing signals (Red > Amber > Green)
    def severity_rank(status: str) -> int:
        return {"Red": 1, "Amber": 2, "Green": 3, "Not Scored": 4}.get(status, 5)
        
    sorted_evidences = sorted(evidences, key=lambda e: severity_rank(e.status))
    
    for e in sorted_evidences:
        if e.status == "Not Scored":
            continue
        lines.append(f"- **{e.signal.replace('_', ' ').title()} ({e.status})**: " + " ".join(e.supporting_facts))
        
    lines.append("")
    
    # 3. Override
    if override_triggered:
        lines.append("> **Note**: Project status escalated to Red due to >30% of open tasks being overdue.")
        
    # 4. Not Scored
    not_scored = [e.signal for e in evidences if e.status == "Not Scored"]
    if not_scored:
        lines.append(f"- **Not Scored**: {', '.join(not_scored)} (Missing required data)")
        
    # 5. Data Confidence
    lines.append(f"- **Data Confidence**: {data_confidence}")
    if data_confidence in ["Medium", "Low"]:
        lines.append("  (Lower confidence is due to a high proportion of inferred or missing fields in the source data.)")
        
    return "\n".join(lines)
