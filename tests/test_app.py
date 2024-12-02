import pytest
from unittest.mock import patch, MagicMock

import sys
import os

# Importing from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
# Import the functions to test
from app import (
    _configure_page,
    _apply_custom_css,
    _get_proficiency_label,
    _render_skills,
    _create_skills_chart,
    _render_recommendation,
    _render_strengths,
    _render_skill_gaps,
)


# Fixture for session state
@pytest.fixture
def mock_session_state():
    """Create a mock session state for testing."""

    class MockSessionState:
        def __init__(self):
            self.insights_prompt = "Test prompt"
            self.page_filter = "@PAGERANGE(1-3)"

    return MockSessionState()


# Fixture for candidate insights
@pytest.fixture
def sample_candidate_insights():
    """Provide sample candidate insights for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "skills": [
            {"name": "Python", "proficiency": 4},
            {"name": "Machine Learning", "proficiency": 3},
        ],
    }


# Fixture for job match assessment
@pytest.fixture
def sample_match_assessment():
    """Provide sample job match assessment for testing."""
    return {
        "percentage_match": 75,
        "overall_recommendation": "Strong Fit",
        "strengths": ["Strong Python skills", "ML background"],
        "potential_skill_gaps": ["Advanced cloud computing"],
    }


def test_configure_page():
    """Test page configuration function."""
    with patch("streamlit.set_page_config") as mock_set_page_config:
        _configure_page()
        mock_set_page_config.assert_called_once_with(
            page_title="Resume Intelligence",
            page_icon="📋",
            layout="wide",
            initial_sidebar_state="expanded",
        )


def test_apply_custom_css():
    """Test custom CSS application."""
    with patch("streamlit.markdown") as mock_markdown:
        _apply_custom_css()
        mock_markdown.assert_called_once()
        # Check that the markdown contains expected CSS
        assert "skill-badge" in mock_markdown.call_args[0][0]


def test_get_proficiency_label():
    """Test proficiency label generation."""
    assert _get_proficiency_label(1) == "Beginner"
    assert _get_proficiency_label(3) == "Intermediate"
    assert _get_proficiency_label(5) == "Advanced"


def test_render_skills():
    """Test skills rendering."""
    skills = [
        {"name": "Python", "proficiency": 4},
        {"name": "JavaScript", "proficiency": 2},
    ]

    with patch("streamlit.markdown") as mock_markdown:
        _render_skills(skills)
        mock_markdown.assert_called_once()
        # Verify skills are rendered
        assert "Python" in mock_markdown.call_args[0][0]
        assert "JavaScript" in mock_markdown.call_args[0][0]


def test_render_skills_empty():
    """Test skills rendering with empty skills list."""
    with patch("streamlit.markdown") as mock_markdown:
        _render_skills([])
        mock_markdown.assert_called_once_with("*No skills listed*")


def test_create_skills_chart(sample_candidate_insights):
    """Test skills proficiency chart creation."""
    with patch("streamlit.subheader"), patch(
        "streamlit.tabs", return_value=(MagicMock(), MagicMock())
    ) as mock_tabs, patch("streamlit.altair_chart"), patch("streamlit.dataframe"):
        _create_skills_chart(sample_candidate_insights["skills"])

        # Verify chart creation steps
        assert mock_tabs.call_count == 1
        # Ensure two tabs are created
        assert len(mock_tabs.call_args[0]) == 1


def test_render_recommendation():
    """Test job match recommendation rendering."""
    sample_assessments = [
        {"overall_recommendation": "Strong Fit"},
        {"overall_recommendation": "Moderate Fit"},
        {"overall_recommendation": "Poor Fit"},
    ]

    for assessment in sample_assessments:
        with patch("streamlit.markdown") as mock_markdown:
            _render_recommendation(assessment)
            mock_markdown.assert_called_once()
            # Verify recommendation is rendered
            assert assessment["overall_recommendation"] in mock_markdown.call_args[0][0]


def test_render_strengths(sample_match_assessment):
    """Test strengths rendering."""
    with patch("streamlit.subheader"), patch(
        "streamlit.columns", return_value=[MagicMock(), MagicMock()]
    ), patch("streamlit.markdown") as mock_markdown:
        _render_strengths(sample_match_assessment)
        mock_markdown.assert_called()
        # Verify strengths are rendered
        assert "ML background" in mock_markdown.call_args[0][0]


def test_render_strengths_empty():
    """Test strengths rendering with empty strengths."""
    with patch("streamlit.subheader"), patch("streamlit.info") as mock_info:
        _render_strengths({"strengths": []})
        mock_info.assert_called_once_with("No specific strengths identified")


def test_render_skill_gaps(sample_match_assessment):
    """Test skill gaps rendering."""
    with patch("streamlit.subheader"), patch(
        "streamlit.columns", return_value=[MagicMock()]
    ), patch("streamlit.markdown") as mock_markdown:
        _render_skill_gaps(sample_match_assessment)
        mock_markdown.assert_called_once()
        # Verify skill gaps are rendered
        assert "Advanced cloud computing" in mock_markdown.call_args[0][0]


def test_render_skill_gaps_empty():
    """Test skill gaps rendering with empty gaps."""
    with patch("streamlit.subheader"), patch("streamlit.info") as mock_info:
        _render_skill_gaps({"potential_skill_gaps": []})
        mock_info.assert_called_once_with("No significant skill gaps identified")


# Additional error handling and edge case tests could be added here
