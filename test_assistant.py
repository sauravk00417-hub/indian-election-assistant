import unittest
from assistant import _is_retryable, build_system_prompt

class TestElectionAssistant(unittest.TestCase):
    
    def test_retry_logic_network_error(self):
        # Test that network errors (429) trigger a retry
        self.assertTrue(_is_retryable(Exception("429 Resource Exhausted")))
        self.assertTrue(_is_retryable(Exception("503 Service Unavailable")))

    def test_retry_logic_auth_error(self):
        # Test that missing API keys do NOT trigger a retry
        self.assertFalse(_is_retryable(ValueError("GOOGLE_API_KEY not set")))
        
    def test_build_system_prompt(self):
        # Test that the knowledge base is correctly injected into the prompt
        mock_kb = "VOTER REGISTRATION: Minimum age 18."
        prompt = build_system_prompt(mock_kb)
        self.assertIn("VOTER REGISTRATION", prompt)
        self.assertIn("CRITICAL LANGUAGE RULE", prompt)

if __name__ == '__main__':
    unittest.main()
