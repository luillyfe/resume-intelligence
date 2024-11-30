import requests
import os
from typing import Dict, Any, Optional


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


# Ensure script only runs when directly executed
if __name__ == "__main__":
    result = generate_insights("./resume.pdf")

    if result:
        print("AI agent processed the document successfully:")
        print(result)
