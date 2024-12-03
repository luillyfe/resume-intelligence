import streamlit as st
import requests
import os
import json
from typing import Dict, Any, Optional


@st.cache_data
def process_document_with_ai_agent(
    agent_id: str,
    bearer_token: str,
    pdf_path: str,
    instruction: str = "Please extract actionable insights from the candidates' resume",
    page_range: str = "@PAGERANGE(1-3)",
) -> Optional[Dict[Any, Any]]:
    """
    Process a PDF document using a specified Roe AI agent with a given instruction.

    :param agent_id: The unique identifier for the Roe AI agent
    :param bearer_token: Authentication token for the Roe AI API
    :param pdf_path: Path to the PDF file to be processed
    :param instruction: Custom instruction for the AI agent (default focuses on resume insights)
    :param page_range: Specify which pages of the PDF to process (default: first 3 pages)
    :return: JSON response from the API or None if an error occurs
    """
    # API endpoint
    url = f"https://api.roe-ai.com/v1/agents/run/{agent_id}/"

    # Prepare the multipart/form-data payload
    data = {"instruction": instruction, "page_filter": page_range}

    try:
        # Open the file in binary mode for upload
        with open(pdf_path, "rb") as pdf_file:
            # Prepare files payload
            files = {
                "pdf_file": (os.path.basename(pdf_path), pdf_file, "application/pdf")
            }

            # Headers with authorization
            headers = {"Authorization": f"Bearer {bearer_token}"}

            # Send POST request
            response = requests.post(url, data=data, files=files, headers=headers)

            # Check the response
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Return the response content
            return response.json()

    except FileNotFoundError:
        print(f"Error: Document file not found at {pdf_path}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None
    except ValueError as e:
        print(f"Error processing response: {e}")
        return None


@st.cache_data
def process_url_with_ai_agent(
    agent_id: str, bearer_token: str, data: Dict[str, str]
) -> Optional[Dict[Any, Any]]:
    """
    Process a URL with a Roe AI agent.

    :param agent_id: The unique identifier for the Roe AI agent
    :param bearer_token: Authentication token for the Roe AI API
    :param url: The URL to be processed
    :param data: A dictionary of parameters for the AI agent
    :return: JSON response from the API or None if an error occurs
    """
    # API endpoint
    url = f"https://api.roe-ai.com/v1/agents/run/{agent_id}/"

    try:
        # Headers with authorization
        headers = {"Authorization": f"Bearer {bearer_token}"}

        # Send POST request
        response = requests.post(url, data=data, headers=headers)

        # Check the response
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Return the response content
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None
    except ValueError as e:
        print(f"Error processing response: {e}")
        return None


@st.cache_data
def process_text_with_ai_agent(
    agent_id: str, bearer_token: str, data: Dict[str, str]
) -> Optional[Dict[Any, Any]]:
    """
    Process text data using the job description parser Roe AI agent via API.

    This function sends a POST request to the Roe AI agent API with the provided
    text data and authentication credentials. It is designed to process and
    analyze text through a specified AI agent.

    :param agent_id: The unique identifier for the Roe AI agent to be used
    :param bearer_token: Authentication token for accessing the Roe AI API
    :param data: A dictionary containing the text data and any additional
                 parameters required by the AI agent. Typically includes
                 'prompt' and 'target' keys.

    :return: A dictionary containing the JSON response from the AI agent
             if the request is successful, or None if an error occurs.

    :raises requests.exceptions.RequestException: If there's an error
            connecting to or communicating with the Roe AI API
    :raises ValueError: If there's an error processing the API response

    Example:
        data = {
            'prompt': 'Analyze the following text',
            'target': 'Some text to be processed'
        }
        result = process_text_with_ai_agent(
            'agent123', 'bearer_token_value', data
        )
    """
    # API endpoint
    url = f"https://api.roe-ai.com/v1/agents/run/{agent_id}/"

    try:
        # Headers with authorization
        headers = {"Authorization": f"Bearer {bearer_token}"}

        # Send POST request
        response = requests.post(url, data=data, headers=headers)

        # Check the response
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Return the response content
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None
    except ValueError as e:
        print(f"Error processing response: {e}")
        return None


def evaluate_candidate_job_fit(
    candidate_insights: str,
    job_details: str,
) -> Optional[Dict[Any, Any]]:
    """
    Evaluate how well a candidate matches a specific job's requirements.

    :param candidate_insights: Extracted insights from the candidate's resume
    :param job_details: Details of the job description
    :return: Detailed matching assessment or None if processing fails
    """
    # Retrieve credentials from environment variables
    AGENT_ID = os.environ.get("ROE_AI_EVALUATE_AGENT")
    BEARER_TOKEN = os.environ.get("ROE_AI_BEARER_TOKEN")

    # Validate credentials
    if not AGENT_ID or not BEARER_TOKEN:
        print(
            "Error: ROE_AI_EVALUATE_AGENT or ROE_AI_BEARER_TOKEN not set in environment variables"
        )
        return

    # Prepare data for the AI agent
    data = {
        "prompt": (
            "Perform a comprehensive assessment of how well the candidate matches "
            "the job requirements. Provide a detailed analysis including:"
            "1. Percentage match of skills and experience"
            "2. Strengths that align with the job"
            "3. Potential skill gaps"
            "4. Overall recommendation (Strong Fit/Moderate Fit/Weak Fit)"
            'output example: {"percentage_match": 75, "overall_recommendation": "Strong Fit", "strengths": ["Strong Python skills", "ML background"], "potential_skill_gaps": ["Advanced cloud computing"]}'
        ),
        "target": (
            f"Candidate Insights:\n{json.dumps(candidate_insights)}\n\n"
            f"Job Details:\n{json.dumps(job_details)}"
        ),
    }

    try:
        # Process the matching assessment
        result = process_text_with_ai_agent(AGENT_ID, BEARER_TOKEN, data)

        if result is None:
            raise ValueError("Failed to process candidate-job matching")

        return result
    except Exception as e:
        print(f"Error assessing candidate-job match: {e}")
        return None


def generate_insights(pdf_path: str, instruction: str, page_range: str):
    """
    Main function to demonstrate processing a document with a Roe AI agent.
    Reads credentials from environment variables.
    """
    # Retrieve credentials from environment variables
    AGENT_ID = os.environ.get("ROE_AI_AGENT_ID")
    BEARER_TOKEN = os.environ.get("ROE_AI_BEARER_TOKEN")

    # Validate credentials
    if not AGENT_ID or not BEARER_TOKEN:
        print(
            "Error: ROE_AI_AGENT_ID or ROE_AI_BEARER_TOKEN not set in environment variables"
        )
        return

    # Process document
    return process_document_with_ai_agent(
        AGENT_ID, BEARER_TOKEN, pdf_path, instruction, page_range
    )


def extract_job_details(
    url: str = "https://www.ycombinator.com/companies/roe-ai/jobs/NZDmSo9-founding-engineer",
    form_selector: str = "#job-description-form",
    form_fields: Dict[str, str] = None,
):
    """
    Extract job description from a given URL, optionally submitting form fields.

    :param url: URL to process
    :param form_selector: CSS selector for the form to interact with
    :param form_fields: Dictionary of form field names and their values
    :return: Processed job description or None
    """
    # Retrieve credentials from environment variables
    AGENT_ID = os.environ.get("ROE_AI_JOB_AGENT")
    BEARER_TOKEN = os.environ.get("ROE_AI_BEARER_TOKEN")

    # Validate credentials
    if not AGENT_ID or not BEARER_TOKEN:
        print("Error: Credentials not set")
        return None

    # Prepare data for the AI agent
    data = {
        "url": url,
        "instruction": "Extract key responsibilities and requirements from this job description",
        "form_selector": form_selector,
        "form_fields": json.dumps(form_fields) if form_fields else "",
    }

    try:
        # Process the URL
        result = process_url_with_ai_agent(AGENT_ID, BEARER_TOKEN, data)

        if result is None:
            raise ValueError("Failed to process URL")

        return result
    except Exception as e:
        print(f"Error extracting job description: {e}")
        return None


# Ensure script only runs when directly executed
if __name__ == "__main__":
    result = generate_insights("./resume.pdf")

    if result:
        print("AI agent processed the document successfully:")
        print(result)


# https://docs.streamlit.io/develop/concepts/architecture/caching
# https://docs.roe-ai.com/api-reference/agents/run
# https://docs.roe-ai.com/agents/introduction