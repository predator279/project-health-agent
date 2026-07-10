import json
import os
import yaml
from datetime import date
from collections import defaultdict
from src.parsers import XlsxAdapter
from src.scoring import score_schedule_slippage, score_milestone_health, score_blockers, score_budget_burn
from src.scoring import rollup_phase, rollup_project, compute_data_confidence
from src.evidence import compose_narrative

def load_config(config_path: str = "config/rag_thresholds.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def generate_weekly_report(input_file: str, output_dir: str, config_path: str = "config/rag_thresholds.yaml"):
    cfg = load_config(config_path)
    today = date.today()
    
    # Extract project ID from filename
    filename = os.path.basename(input_file)
    project_id = filename.replace(".xlsx", "").replace(" ", "_")
    
    # Parse file
    adapter = XlsxAdapter()
    plan = adapter.parse(input_file, project_id)
    
    # Score tasks and phases
    all_evidences = []
    phase_tasks = defaultdict(list)
    
    for task in plan.tasks:
        if task.phase_milestone:
            phase_tasks[task.phase_milestone].append(task)
            
        evidences = [
            score_schedule_slippage(task, cfg, today),
            score_blockers(task, plan.comments, cfg, None)
        ]
        
        burn_ev = score_budget_burn(task, cfg)
        if burn_ev:
            evidences.append(burn_ev)
            
        all_evidences.extend(evidences)
        
    # Score milestones/phases
    phase_statuses = {}
    for phase, tasks in phase_tasks.items():
        phase_ev = score_milestone_health(tasks, cfg, today)
        all_evidences.append(phase_ev)
        
        # Rollup phase
        phase_related_evs = [e for e in all_evidences if e.signal == "milestone_health" or (hasattr(e, "task_id") and e.task_id in [t.task_id for t in tasks])] 
        # (Simplified phase rollup logic for this exercise)
        phase_statuses[phase] = rollup_phase(tasks, [phase_ev])
        
    # Rollup project
    project_status, override = rollup_project(phase_statuses, plan.tasks, cfg)
    
    # Data Confidence
    confidence = compute_data_confidence(plan.tasks)
    
    # Compose Narrative
    narrative = compose_narrative(project_status, all_evidences, override, confidence)
    
    # Prepare Output
    output_data = {
        "project_id": project_id,
        "date": str(today),
        "status": project_status,
        "confidence": confidence,
        "override_triggered": override,
        "summary": plan.summary.model_dump(mode='json'),
        "narrative": narrative,
        "evidences": [e.model_dump(mode='json') for e in all_evidences]
    }
    
    # Ensure output directories exist
    proj_out_dir = os.path.join(output_dir, project_id)
    os.makedirs(proj_out_dir, exist_ok=True)
    
    # Write JSON
    json_path = os.path.join(proj_out_dir, f"{today}.json")
    with open(json_path, "w") as f:
        json.dump(output_data, f, indent=2)
        
    # Write latest JSON symlink (or just copy)
    latest_json_path = os.path.join(proj_out_dir, "latest.json")
    with open(latest_json_path, "w") as f:
        json.dump(output_data, f, indent=2)
        
    # Write Markdown
    md_path = os.path.join(proj_out_dir, f"{today}.md")
    with open(md_path, "w") as f:
        md_content = f"# Weekly Health Report: {plan.summary.project_name}\n\n"
        md_content += f"**Date:** {today}\n\n"
        md_content += f"**Project Manager:** {plan.summary.project_manager or 'Unknown'}\n\n"
        md_content += "---\n\n"
        md_content += narrative
        f.write(md_content)
        
    return json_path, md_path
