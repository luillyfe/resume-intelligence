import unittest
from unittest.mock import patch, mock_open, MagicMock
import requests
import json

# Importing from parent directory
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
# Import the roe_ai
import roe_ai


class TestRoeAIModule(unittest.TestCase):
    def setUp(self):
        """
        Set up test environment before each test method.
        """
        # Mock environment variables
        self.mock_env_patcher = patch.dict(
            os.environ,
            {
                "ROE_AI_AGENT_ID": "test_agent_id",
                "ROE_AI_BEARER_TOKEN": "test_bearer_token",
                "ROE_AI_EVALUATE_AGENT": "test_evaluate_agent",
                "ROE_AI_JOB_AGENT": "test_job_agent",
            },
        )
        self.mock_env_patcher.start()

    def tearDown(self):
        """
        Clean up after each test method.
        """
        self.mock_env_patcher.stop()

    @patch("requests.post")
    def test_process_document_with_ai_agent_success(self, mock_post):
        """
        Test successful document processing with AI agent.
        """
        # Prepare mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "document processed"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Mock file opening
        with patch("builtins.open", mock_open(read_data=b"dummy pdf content")):
            result = roe_ai.process_document_with_ai_agent(
                "test_agent_id", "test_token", "test_path.pdf"
            )

        # Assertions
        self.assertEqual(result, {"result": "document processed"})
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_process_document_with_ai_agent_file_not_found(self, mock_post):
        """
        Test document processing when file is not found.
        """
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = roe_ai.process_document_with_ai_agent(
                "test_agent_id", "test_token", "non_existent.pdf"
            )

        # Assertions
        self.assertIsNone(result)
        mock_post.assert_not_called()

    @patch("requests.post")
    def test_process_text_with_ai_agent_success(self, mock_post):
        """
        Test successful text processing with AI agent.
        """
        # Prepare mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "text processed"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Prepare test data
        test_data = {"prompt": "Test prompt success", "target": "Test target text"}

        result = roe_ai.process_text_with_ai_agent(
            "test_agent_id", "test_token", test_data
        )

        # Assertions
        self.assertEqual(result, {"result": "text processed"})
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_process_text_with_ai_agent_request_exception(self, mock_post):
        """
        Test text processing when a request exception occurs.
        """
        # Simulate request exception
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        # Prepare test data
        test_data = {"prompt": "Test prompt", "target": "Test target text"}

        result = roe_ai.process_text_with_ai_agent(
            "test_agent_id", "test_token", test_data
        )

        # Assertions
        self.assertIsNone(result)

    @patch("roe_ai.process_text_with_ai_agent")
    def test_evaluate_candidate_job_fit_success(self, mock_process):
        """
        Test candidate job fit evaluation.
        """
        # Prepare mock response
        mock_process.return_value = {
            "match_percentage": 85,
            "recommendation": "Strong Fit",
        }

        # Prepare test data
        candidate_insights = {"skills": ["Python", "ML"]}
        job_details = {"requirements": ["Python", "Machine Learning"]}

        result = roe_ai.evaluate_candidate_job_fit(candidate_insights, job_details)

        # Assertions
        self.assertIsNotNone(result)
        mock_process.assert_called_once()

    @patch("roe_ai.process_url_with_ai_agent")
    def test_extract_job_details_success(self, mock_process):
        """
        Test job details extraction.
        """
        # Prepare mock response
        mock_process.return_value = {
            "job_description": "Founding Engineer role",
            "key_requirements": ["Python", "ML"],
        }

        # Test extraction
        result = roe_ai.extract_job_details()

        # Assertions
        self.assertIsNotNone(result)
        mock_process.assert_called_once()

    def test_evaluate_candidate_job_fit_missing_credentials(self):
        """
        Test job fit evaluation with missing credentials.
        """
        # Temporarily remove environment variables
        with patch.dict(os.environ, {}, clear=True):
            result = roe_ai.evaluate_candidate_job_fit(
                "candidate insights", "job details"
            )

            # Assertions
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
