import streamlit as st
import json
import tempfile
import pandas as pd
import altair as alt
from typing import Dict, Any, Optional

from roe_ai import generate_insights, extract_job_details, evaluate_candidate_job_fit


class ResumeIntelligenceApp:
    """
    A Streamlit application for processing and analyzing resumes using Roe AI.
    """

    def __init__(self):
        """
        Initialize the Streamlit application with configuration and styling.
        """
        self._configure_page()
        self._apply_custom_css()

    def _configure_page(self):
        """
        Set up the Streamlit page configuration.
        """
        st.set_page_config(
            page_title="Resume Intelligence",
            page_icon="📋",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    def _apply_custom_css(self):
        """
        Apply custom CSS styling to the Streamlit application.
        """
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

    def run(self):
        """
        Main method to run the Streamlit application.
        """
        self._render_title()
        self._configure_sidebar()

        uploaded_file = self._upload_resume()

        if uploaded_file is not None:
            self._process_resume(uploaded_file)

    def _render_title(self):
        """
        Render the application title and description.
        """
        st.title("📄 Resume Insights with Roe AI")
        st.write("Upload a PDF document to process with our AI agent.")

    def _configure_sidebar(self):
        """
        Configure the sidebar with application settings.
        """
        st.sidebar.header("🔧 Configuration")

        default_instruction = (
            "Please extract actionable insights from the candidates resume"
        )

        st.session_state.insights_prompt = st.sidebar.text_area(
            "AI Agent Instruction", value=default_instruction, height=150, disabled=True
        )

        st.session_state.page_filter = st.sidebar.text_input(
            "Page Range to Process", value="@PAGERANGE(1-3)", disabled=True
        )

    def _upload_resume(self):
        """
        Handle resume file upload.

        Returns:
            Uploaded file or None
        """
        return st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document to process with the Roe AI agent",
        )

    def _process_resume(self, uploaded_file):
        """
        Process the uploaded resume and display insights.

        Args:
            uploaded_file: Uploaded PDF file
        """
        if st.button("Extract Resume Insights", type="primary"):
            insights = self._extract_resume_insights(uploaded_file)
            st.session_state.insights = insights

        if hasattr(st.session_state, "insights"):
            self._display_candidate_profile(st.session_state.insights)
            self._setup_job_description_section(st.session_state.insights)

    def _extract_resume_insights(self, uploaded_file):
        """
        Extract insights from the uploaded resume.

        Args:
            uploaded_file: Uploaded PDF file

        Returns:
            Extracted insights or None
        """
        with st.spinner("Analyzing resume..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_file_path = temp_file.name

                result = generate_insights(
                    temp_file_path,
                    st.session_state.insights_prompt,
                    st.session_state.page_filter,
                )

                insights = json.loads(result[0]["value"])

                # Validate insights against expected schema
                required_fields = ["name", "email", "skills"]
                if all(field in insights for field in required_fields):
                    st.success("Resume processed successfully!")
                    return insights

                st.warning("Received response does not match expected schema.")
                return None

    def _setup_job_description_section(self, insights):
        """
        Set up the job description extraction section.

        Args:
            insights: Candidate insights dictionary
        """
        st.sidebar.header("🌐 Job Description Extraction")
        job_url = st.sidebar.text_input(
            "Job Description URL",
            placeholder="Enter URL of job description",
            help="Paste the URL of a job description to extract details",
        )

        job_details = self._extract_job_details(job_url)

        if job_details:
            self._assess_job_match(job_details, insights)

    def _extract_job_details(self, job_url):
        """
        Extract job details from the provided URL.

        Args:
            job_url: URL of the job description

        Returns:
            Job details dictionary or None
        """
        if job_url:
            if st.button("Extract Job Details", type="primary"):
                with st.spinner("Extracting job description..."):
                    try:
                        result = extract_job_details(job_url)
                        job_details = json.loads(result[0]["value"])
                        st.session_state.job_details = job_details
                        st.success("Job description extracted successfully!")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")

            if hasattr(st.session_state, "job_details"):
                # Display job details
                st.subheader("📋 Job Description Details")
                st.markdown(
                    st.session_state.job_details.get("result", "No details available")
                )
                return st.session_state.job_details

        return None

    def _assess_job_match(self, job_details, candidate_insights):
        """
        Assess the job match between candidate insights and job details.

        Args:
            job_details: Dictionary of job details
            candidate_insights: Dictionary of candidate insights
        """
        st.sidebar.header("🔍 Job Match Assessment")

        if st.sidebar.button("Assess Job Fit", type="primary"):
            with st.spinner("Analyzing candidate-job match..."):
                try:
                    # Call job matching assessment function
                    result = evaluate_candidate_job_fit(
                        json.dumps(candidate_insights), json.dumps(job_details)
                    )

                    if result:
                        match_assessment = json.loads(result[0]["value"])
                        self._render_job_match_assessment(match_assessment)
                    else:
                        st.error("Failed to assess job fit.")

                except Exception as e:
                    st.error(f"An error occurred during job fit assessment: {str(e)}")

    def _render_job_match_assessment(self, match_assessment):
        """
        Render the detailed job match assessment.

        Args:
            match_assessment: Dictionary containing job match assessment details
        """
        st.header("📊 Candidate-Job Fit Analysis")

        # Overall Match Percentage and Recommendation
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Overall Match",
                value=f"{match_assessment.get('percentage_match', 0)}%",
                help="Percentage of job requirements met by the candidate",
            )

        with col2:
            self._render_recommendation(match_assessment)

        with col3:
            st.metric(
                label="Interview Potential",
                value=(
                    "Good"
                    if match_assessment.get("percentage_match", 0) > 70
                    else "Needs Work"
                ),
                help="Candidate's potential for interview based on job match",
            )

        # Strengths and Skill Gaps
        self._render_strengths(match_assessment)
        self._render_skill_gaps(match_assessment)

        # Full Assessment View
        with st.expander("📄 Detailed Match Assessment"):
            st.json(match_assessment)

    def _render_recommendation(self, match_assessment):
        """
        Render the overall recommendation with color coding.

        Args:
            match_assessment: Dictionary containing job match assessment details
        """
        recommendation = match_assessment.get("overall_recommendation", "Unknown")

        color_map = {
            "Strong Fit": ("green", "✅"),
            "Moderate Fit": ("orange", "⚠️"),
        }

        color, emoji = color_map.get(recommendation, ("red", "❌"))

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

    def _render_strengths(self, match_assessment):
        """
        Render candidate strengths.

        Args:
            match_assessment: Dictionary containing job match assessment details
        """
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

    def _render_skill_gaps(self, match_assessment):
        """
        Render potential skill gaps.

        Args:
            match_assessment: Dictionary containing job match assessment details
        """
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

    def _display_candidate_profile(self, candidate_data: Dict[str, Any]):
        """
        Display a detailed candidate profile.

        Args:
            candidate_data: Dictionary containing candidate information
        """
        st.header(f"🧑‍💼 {candidate_data.get('name', 'Candidate Profile')}")

        # Contact and Skills Overview
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
            self._render_skills(candidate_data.get("skills", []))

        # Skills Proficiency Visualization
        self._create_skills_chart(candidate_data.get("skills", []))

        # Full JSON Response
        with st.expander("📄 Full JSON Response"):
            st.json(candidate_data)

    def _render_skills(self, skills):
        """
        Render skills with badges and proficiency.

        Args:
            skills: List of skill dictionaries
        """
        if skills:
            skills_html = ""
            for skill in skills:
                skill_name = skill.get("name", "Unnamed Skill")
                proficiency = skill.get("proficiency")

                if proficiency is not None:
                    proficiency_label = self._get_proficiency_label(proficiency)
                    skills_html += (
                        f'<span class="skill-badge">{skill_name}'
                        f'<span class="skill-proficiency">{proficiency_label}</span>'
                        f"</span> "
                    )
                else:
                    skills_html += f'<span class="skill-badge">{skill_name}</span> '

            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.markdown("*No skills listed*")

    def _get_proficiency_label(self, proficiency):
        """
        Get a readable proficiency label.

        Args:
            proficiency: Numeric proficiency level

        Returns:
            Proficiency label as a string
        """
        if proficiency <= 2:
            return "Beginner"
        elif proficiency <= 4:
            return "Intermediate"
        else:
            return "Advanced"

    def _create_skills_chart(self, skills):
        """
        Create skills proficiency visualization.

        Args:
            skills: List of skill dictionaries
        """
        st.subheader("📊 Skills Proficiency")

        if skills:
            # Prepare data for the chart
            chart_data = [
                {
                    "skill": skill.get("name", "Unnamed Skill"),
                    "proficiency": skill.get("proficiency", 0),
                }
                for skill in skills
            ]

            # Convert to DataFrame
            df = pd.DataFrame(chart_data)

            # Create visualization tabs
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


# Run the Streamlit app
if __name__ == "__main__":
    app = ResumeIntelligenceApp()
    app.run()
