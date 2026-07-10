import argparse
import os
import json
from datetime import date
from src.reporting.weekly_report import generate_weekly_report
from src.aggregation import detect_trends, detect_emerging_risks
from src.reporting.deck_builder import create_executive_deck

def main():
    parser = argparse.ArgumentParser(description="Project Health Reporting Agent")
    subparsers = parser.add_subparsers(dest="command")
    
    # Weekly Command
    weekly_parser = subparsers.add_parser("run-weekly", help="Generate weekly report for a project plan")
    weekly_parser.add_argument("--input", required=True, help="Path to input Excel file")
    weekly_parser.add_argument("--out", required=True, help="Output directory for reports")
    
    # Monthly Command (Placeholder)
    monthly_parser = subparsers.add_parser("run-monthly", help="Generate monthly executive deck")
    monthly_parser.add_argument("--inputs", required=True, nargs="+", help="Path to latest.json files")
    monthly_parser.add_argument("--out", required=True, help="Output directory for presentation")
    
    args = parser.parse_args()
    
    if args.command == "run-weekly":
        if not os.path.exists(args.input):
            print(f"Error: Input file {args.input} does not exist.")
            return
            
        print(f"Running weekly report for {args.input}...")
        json_path, md_path = generate_weekly_report(args.input, args.out)
        print(f"Report generated successfully!")
        print(f"JSON: {json_path}")
        print(f"Markdown: {md_path}")
        
    elif args.command == "run-monthly":
        print("Generating monthly executive deck...")
        project_reports = []
        for inp in args.inputs:
            if not os.path.exists(inp):
                print(f"Warning: {inp} does not exist, skipping.")
                continue
            with open(inp, "r") as f:
                project_reports.append(json.load(f))
                
        if not project_reports:
            print("Error: No valid input reports found.")
            return
            
        trends = detect_trends(project_reports, {})
        risks = detect_emerging_risks(project_reports, None)
        
        os.makedirs(args.out, exist_ok=True)
        out_path = os.path.join(args.out, f"{date.today()}_executive_deck.pptx")
        
        create_executive_deck(project_reports, trends, risks, out_path)
        print(f"Monthly deck generated successfully at {out_path}")

if __name__ == "__main__":
    main()
