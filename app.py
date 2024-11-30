import streamlit as st
import json
import tempfile
import pandas as pd
import altair as alt
from typing import Dict, Any

from roe_ai import generate_insights


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
    page_range = st.sidebar.text_input("Page Range to Process", value="@PAGERANGE(1-3)", disabled=True)

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


# Run the Streamlit app
if __name__ == "__main__":
    main()
