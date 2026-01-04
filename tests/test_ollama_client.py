import unittest
from unittest.mock import patch, MagicMock
from src.body.ollama_client import OllamaClient
import requests

class TestOllamaClient(unittest.TestCase):
    
    @patch('src.body.ollama_client.requests.get')
    def test_is_alive_success(self, mock_get):
        # Setup mock for 200 OK
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        self.assertTrue(client.is_alive())
        
    @patch('src.body.ollama_client.requests.get')
    def test_is_alive_failure(self, mock_get):
        # Setup mock for Exception
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        client = OllamaClient()
        self.assertFalse(client.is_alive())

    @patch('src.body.ollama_client.requests.post')
    def test_generate_success_streaming(self, mock_post):
        # Setup mock to return an iterator of lines (streaming)
        mock_response = MagicMock()
        mock_response.iter_lines.return_value = [
            b'{"response": "Hello"}',
            b'{"response": " world"}',
            b'{"response": "", "done": true}'
        ]
        mock_post.return_value.__enter__.return_value = mock_response
        
        client = OllamaClient()
        result = client.generate("Hi")
        
        self.assertEqual(result, "Hello world")
        
    @patch('src.body.ollama_client.requests.post')
    def test_generate_failure(self, mock_post):
        # Setup mock to raise Timeout
        mock_post.side_effect = requests.exceptions.Timeout("Timed out")
        
        client = OllamaClient()
        result = client.generate("Hi")
        
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
