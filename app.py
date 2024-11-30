import streamlit as st
import json
import tempfile
import pandas as pd
import altair as alt
from typing import Dict, Any, Optional

from roe_ai import generate_insights, extract_job_details, evaluate_candidate_job_fit


def main():
    """
    Streamlit application for processing documents with a Roe AI agent.
    """
    # Set page config
    st.set_page_config(
        page_title="Resume Intelligence",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for enhanced styling
    st.markdown(
        """
    <style>
    .stButton>button {
        background-color: #4CAF50;
        border-color: white;
        color: white;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .stBadge {
        background-color: #e1f5fe;
        color: #0277bd;
        padding: 5px 10px;
        border-radius: 20px;
        margin: 2px;
        display: inline-block;
    }
    .skill-badge {
        display: inline-flex;
        align-items: center;
        background-color: #e1f5fe;
        color: #0277bd;
        padding: 5px 10px;
        border-radius: 20px;
        margin: 2px;
    }
    .skill-proficiency {
        margin-left: 5px;
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 2px 6px;
        font-size: 0.8em;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Title and description
    st.title("📄 Resume Insights with Roe AI")
    st.write("Upload a PDF document to process with our AI agent.")

    # Sidebar for configuration
    st.sidebar.header("🔧 Configuration")

    # Instruction input
    default_instruction = (
        "Please extract actionable insights from the candidates resume"
    )
    instruction = st.sidebar.text_area(
        "AI Agent Instruction", value=default_instruction, height=150, disabled=True
    )

    # Page range input
    page_range = st.sidebar.text_input(
        "Page Range to Process", value="@PAGERANGE(1-3)", disabled=True
    )

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document to process with the Roe AI agent",
    )

    # Process button and logic
    if uploaded_file is not None:
        # Process button
        if st.button("Extract Resume Insights", type="primary"):
            with st.spinner("Analyzing resume..."):
                # Temporary file handling
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_file_path = temp_file.name
                    # Call the processing function
                    result = generate_insights(temp_file_path, instruction, page_range)
                    insights = json.loads(result[0]["value"])
                    # Let's save insights in cache
                    if "insights" not in st.session_state:
                        st.session_state.insights = insights

            # Display results
            if "error" in result:
                st.error("Failed to process the resume.")
            else:
                # Validate against expected schema
                required_fields = ["name", "email", "skills"]
                if all(field in insights for field in required_fields):
                    st.success("Resume processed successfully!")
                    display_candidate_profile(insights)

                else:
                    st.warning("Received response does not match expected schema.")
                    st.json(insights)

        if hasattr(st.session_state, "insights"):
            display_candidate_profile(st.session_state.insights)
            # Add a new section for job description extraction
            st.sidebar.header("🌐 Job Description Extraction")
            job_url = st.sidebar.text_input(
                "Job Description URL",
                placeholder="Enter URL of job description",
                help="Paste the URL of a job description to extract details",
            )

            display_job_details(job_url)

        # If job details are already in session state, prepare for job match
        if hasattr(st.session_state, "job_details") and hasattr(
            st.session_state, "insights"
        ):
            display_job_match_assessment(
                st.session_state.job_details, st.session_state.insights
            )


def display_candidate_profile(candidate_data: Dict[str, Any]):
    """
    Create a beautiful, informative display of candidate profile with improved chart organization

    :param candidate_data: Dictionary containing candidate information
    """
    # Profile header with name and contact
    st.header(f"🧑‍💼 {candidate_data.get('name', 'Candidate Profile')}")

    # Create more responsive columns
    col1, col2 = st.columns([1, 2])

    with col1:
        # Contact Information
        st.subheader("📧 Contact Information")
        st.markdown(f"**Email:** {candidate_data.get('email', 'Not provided')}")

        # Age (if available)
        if "age" in candidate_data:
            st.markdown(f"**Age:** {candidate_data['age']}")

    with col2:
        # Skills Section
        st.subheader("🛠️ Skills Overview")
        if candidate_data.get("skills"):
            skills_html = ""
            for skill in candidate_data["skills"]:
                # Generate skill badge with proficiency
                skill_name = skill.get("name", "Unnamed Skill")
                proficiency = skill.get("proficiency")

                # Create skill badge with optional proficiency
                if proficiency is not None:
                    # Map proficiency to a readable level
                    def get_proficiency_label(prof):
                        if prof <= 2:
                            return "Beginner"
                        elif prof <= 4:
                            return "Intermediate"
                        else:
                            return "Advanced"

                    skills_html += (
                        f'<span class="skill-badge">{skill_name}'
                        f'<span class="skill-proficiency">{get_proficiency_label(proficiency)}</span>'
                        f"</span> "
                    )
                else:
                    skills_html += f'<span class="skill-badge">{skill_name}</span> '

            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.markdown("*No skills listed*")

    # Skills Proficiency Visualization
    st.subheader("📊 Skills Proficiency")
    if candidate_data.get("skills"):
        # Prepare data for the chart
        chart_data = []
        for skill in candidate_data["skills"]:
            skill_name = skill.get("name", "Unnamed Skill")
            proficiency = skill.get("proficiency", 0)
            chart_data.append({"skill": skill_name, "proficiency": proficiency})

        # Convert to DataFrame
        df = pd.DataFrame(chart_data)

        # Create two visualization options
        tab1, tab2 = st.tabs(["Bar Chart", "Table View"])

        with tab1:
            # Altair Bar Chart with improved styling
            chart = (
                alt.Chart(df)
                .mark_bar(
                    color="#4CAF50",  # Green color to match other design elements
                    opacity=0.7,
                )
                .encode(
                    x=alt.X("skill:N", title="Skills", sort="-y"),
                    y=alt.Y(
                        "proficiency:Q",
                        title="Proficiency Level",
                        scale=alt.Scale(domain=[0, max(df["proficiency"]) * 1.2]),
                    ),
                    tooltip=["skill", "proficiency"],
                )
                .properties(width=600, height=400, title="Skills Proficiency Breakdown")
                .configure_title(fontSize=16, font="Arial", anchor="middle")
            )

            st.altair_chart(chart, use_container_width=True)

        with tab2:
            # Enhanced Table View
            styled_df = df.style.background_gradient(
                cmap="Greens", subset=["proficiency"]
            )
            st.dataframe(styled_df, use_container_width=True)

    # Expandable section for full JSON
    with st.expander("📄 Full JSON Response"):
        st.json(candidate_data)


def display_job_details(job_url: str) -> Optional[Dict[str, Any]]:
    # Job Description Extraction Section
    job_details = None
    if job_url:
        if st.button("Extract Job Details", type="primary"):
            with st.spinner("Extracting job description..."):
                try:
                    # Call the job description extraction function
                    if "job_details" not in st.session_state:
                        result = extract_job_details(job_url)
                        # Parse the result
                        job_details = json.loads(result[0]["value"])
                        # Store job details in session state
                        st.session_state.job_details = job_details

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    return None
        if hasattr(st.session_state, "job_details"):
            # Display the extracted job details
            st.success("Job description extracted successfully!")

            # Display key sections
            st.subheader("📋 Job Description Details")
            st.markdown(st.session_state.job_details["result"])

            # Expandable full JSON view
            with st.expander("📄 Full Job Description JSON"):
                st.json(st.session_state.job_details)

            return st.session_state.job_details
    else:
        st.info("Please enter a job description URL in the sidebar.")

    return None


def display_job_match_assessment(
    job_details: Dict[str, Any], candidate_insights: Dict[str, Any]
):
    """
    Display the assessment of how well a candidate matches a job description with enhanced visualization.

    :param job_details: Dictionary containing job description details
    :param candidate_insights: Dictionary containing candidate insights
    """
    st.sidebar.header("🔍 Job Match Assessment")

    # Check if both job details and candidate insights are available
    if job_details and candidate_insights:
        if st.sidebar.button("Assess Job Fit", type="primary"):
            with st.spinner("Analyzing candidate-job match..."):
                try:
                    # Call the job matching assessment function
                    result = evaluate_candidate_job_fit(
                        json.dumps(candidate_insights), json.dumps(job_details)
                    )

                    if result:
                        # Parse the result
                        match_assessment = json.loads(result[0]["value"])

                        # Create a visually appealing job fit assessment
                        st.header("📊 Candidate-Job Fit Analysis")

                        # Overall Match Percentage
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                label="Overall Match",
                                value=f"{match_assessment.get('percentage_match', 0)}%",
                                help="Percentage of job requirements met by the candidate",
                            )

                        with col2:
                            # Recommendation color coding
                            recommendation = match_assessment.get(
                                "overall_recommendation", "Unknown"
                            )
                            if recommendation == "Strong Fit":
                                color = "green"
                                emoji = "✅"
                            elif recommendation == "Moderate Fit":
                                color = "orange"
                                emoji = "⚠️"
                            else:
                                color = "red"
                                emoji = "❌"

                            st.markdown(
                                f"""
                            <div style="background-color:{color}20; 
                                        border-radius:10px; 
                                        padding:10px; 
                                        text-align:center;">
                            <h4 style="color:{color};">
                            {emoji} {recommendation}
                            </h4>
                            </div>
                            """,
                                unsafe_allow_html=True,
                            )

                        with col3:
                            # Potential interview readiness
                            st.metric(
                                label="Interview Potential",
                                value=(
                                    "Good"
                                    if match_assessment.get("percentage_match", 0) > 70
                                    else "Needs Work"
                                ),
                                help="Candidate's potential for interview based on job match",
                            )

                        # Strengths Section
                        st.subheader("🌟 Candidate Strengths")
                        strengths = match_assessment.get("strengths", [])
                        if strengths:
                            strength_cols = st.columns(3)
                            for i, strength in enumerate(strengths):
                                with strength_cols[i % 3]:
                                    st.markdown(
                                        f"""
                                    <div style="background-color:#e6f3e6; 
                                                border-left: 4px solid green; 
                                                padding: 10px; 
                                                margin-bottom: 10px; 
                                                border-radius: 5px;">
                                    {strength}
                                    </div>
                                    """,
                                        unsafe_allow_html=True,
                                    )
                        else:
                            st.info("No specific strengths identified")

                        # Potential Skill Gaps Section
                        st.subheader("🚧 Potential Skill Gaps")
                        skill_gaps = match_assessment.get("potential_skill_gaps", [])
                        if skill_gaps:
                            gap_cols = st.columns(3)
                            for i, gap in enumerate(skill_gaps):
                                with gap_cols[i % 3]:
                                    st.markdown(
                                        f"""
                                    <div style="background-color:#fee6e6; 
                                                border-left: 4px solid red; 
                                                padding: 10px; 
                                                margin-bottom: 10px; 
                                                border-radius: 5px;">
                                    {gap}
                                    </div>
                                    """,
                                        unsafe_allow_html=True,
                                    )
                        else:
                            st.info("No significant skill gaps identified")

                        # Expandable full assessment view
                        with st.expander("📄 Detailed Match Assessment"):
                            st.json(match_assessment)

                    else:
                        st.error("Failed to assess job fit.")

                except Exception as e:
                    st.error(f"An error occurred during job fit assessment: {str(e)}")
    else:
        st.sidebar.info("Upload resume and job description to assess job fit.")


# Run the Streamlit app
if __name__ == "__main__":
    main()
