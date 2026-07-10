from src.schema import TaskRecord

def compute_data_confidence(tasks: list[TaskRecord]) -> str:
    total_fields = 0
    direct_fields = 0
    
    for t in tasks:
        for field, conf in t.field_confidence.items():
            total_fields += 1
            if conf == "direct":
                direct_fields += 1
                
    if total_fields == 0:
        return "Low"
        
    prop = direct_fields / total_fields
    if prop >= 0.85:
        return "High"
    elif prop >= 0.60:
        return "Medium"
    else:
        return "Low"
