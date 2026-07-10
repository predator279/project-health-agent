import streamlit as st
import os
import json
import tempfile
from datetime import date

from src.reporting.weekly_report import generate_weekly_report
from src.aggregation import detect_trends, detect_emerging_risks
from src.reporting.deck_builder import create_executive_deck

st.set_page_config(page_title="Project Health Agent", layout="wide")

st.title("📊 Project Health Reporting Agent")
st.markdown("Automated RAG scoring, evidence building, and executive presentation synthesis.")

tab1, tab2 = st.tabs(["Weekly Health Report", "Monthly Executive Deck"])

# --- TAB 1: WEEKLY REPORT ---
with tab1:
    st.header("Generate Weekly Report")
    st.markdown("Upload a Project Plan (Excel) to generate a hallucination-free health narrative.")
    
    uploaded_file = st.file_uploader("Upload Project Plan (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        if st.button("Generate Weekly Report", type="primary"):
            with st.spinner("Parsing file and calculating RAG status..."):
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Save uploaded file
                    input_path = os.path.join(tmpdir, uploaded_file.name)
                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Generate report
                    out_dir = os.path.join(tmpdir, "outputs")
                    os.makedirs(out_dir, exist_ok=True)
                    
                    try:
                        json_path, md_path = generate_weekly_report(input_path, out_dir)
                        
                        st.success("Report generated successfully!")
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.subheader("Narrative Output")
                            with open(md_path, "r") as f:
                                md_content = f.read()
                            st.markdown(md_content)
                            
                        with col2:
                            st.subheader("Structured Evidence (JSON)")
                            with open(json_path, "r") as f:
                                json_content = f.read()
                            st.json(json.loads(json_content), expanded=False)
                            
                            st.download_button(
                                label="Download JSON Report",
                                data=json_content,
                                file_name=os.path.basename(json_path),
                                mime="application/json"
                            )
                            st.download_button(
                                label="Download Markdown Report",
                                data=md_content,
                                file_name=os.path.basename(md_path),
                                mime="text/markdown"
                            )
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")

# --- TAB 2: MONTHLY DECK ---
with tab2:
    st.header("Generate Monthly Executive Deck")
    st.markdown("Upload multiple Weekly JSON reports to aggregate trends and build a PowerPoint presentation.")
    
    uploaded_jsons = st.file_uploader("Upload Weekly Reports (.json)", type=["json"], accept_multiple_files=True)
    
    if uploaded_jsons and len(uploaded_jsons) > 0:
        if st.button("Synthesize Executive Deck", type="primary"):
            with st.spinner("Aggregating trends and building PowerPoint..."):
                project_reports = []
                for json_file in uploaded_jsons:
                    try:
                        data = json.load(json_file)
                        project_reports.append(data)
                    except Exception as e:
                        st.warning(f"Could not parse {json_file.name}: {str(e)}")
                        
                if not project_reports:
                    st.error("No valid reports found.")
                else:
                    try:
                        trends = detect_trends(project_reports, {})
                        risks = detect_emerging_risks(project_reports, None)
                        
                        with tempfile.TemporaryDirectory() as tmpdir:
                            out_path = os.path.join(tmpdir, f"{date.today()}_executive_deck.pptx")
                            create_executive_deck(project_reports, trends, risks, out_path)
                            
                            st.success(f"Successfully generated deck across {len(project_reports)} projects!")
                            
                            with open(out_path, "rb") as f:
                                st.download_button(
                                    label="📥 Download Executive Presentation (.pptx)",
                                    data=f.read(),
                                    file_name=os.path.basename(out_path),
                                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                    type="primary"
                                )
                                
                            st.subheader("Aggregated Trends Detected")
                            if not trends:
                                st.info("No cross-project trends detected.")
                            for t in trends:
                                st.write(f"**{t.category}: {t.signal}** (Affected: {', '.join(t.affected_project_ids)})")
                                
                    except Exception as e:
                        st.error(f"Error generating presentation: {str(e)}")
