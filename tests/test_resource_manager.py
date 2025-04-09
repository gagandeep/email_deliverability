import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
import tempfile
import time
from email_deliverability.resource_manager import ResourceManager


class TestResourceManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a fresh instance for tests
        ResourceManager._instance = None
        ResourceManager._initialized = False
        self.manager = ResourceManager(cache_dir=self.temp_dir)
        
    def tearDown(self):
        # Clean up the temporary directory
        try:
            for filename in os.listdir(self.temp_dir):
                os.unlink(os.path.join(self.temp_dir, filename))
            os.rmdir(self.temp_dir)
        except:
            pass  # Ignore errors in cleanup
        
    def test_singleton_pattern(self):
        # Test that ResourceManager is a singleton
        manager2 = ResourceManager()
        self.assertIs(self.manager, manager2)
    
    @patch('requests.get')
    def test_download_resource(self, mock_get):
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.text = "test_data"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Download a test resource
        result = self.manager.download_resource("test_resource", "http://example.com/test")
        
        # Verify the result
        self.assertEqual("test_data", result)
        
        # Verify the resource was saved
        resource_path = os.path.join(self.temp_dir, "test_resource.json")
        with open(resource_path, 'r') as f:
            saved_data = f.read()
            self.assertEqual("test_data", saved_data)
        
        # Verify last download time was updated
        self.assertIn("test_resource", self.manager.last_download_time)
    
    @patch('requests.get')
    def test_download_with_processor(self, mock_get):
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.text = "item1\nitem2\nitem3"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Create a processor function
        def processor(data):
            return data.strip().split('\n')
        
        # Download with processor
        result = self.manager.download_resource(
            "test_list", 
            "http://example.com/list",
            processor=processor
        )
        
        # Verify the result
        self.assertEqual(["item1", "item2", "item3"], result)
    
    @patch('requests.get')
    def test_download_error_fallback(self, mock_get):
        # Create a cached version first
        cached_data = ["cached_item1", "cached_item2"]
        resource_path = os.path.join(self.temp_dir, "test_resource.json")
        with open(resource_path, 'w') as f:
            json.dump(cached_data, f)
        
        # Set up the mock to simulate a connection error
        mock_get.side_effect = Exception("Connection error")
        
        # Try downloading with an error - should fall back to cached
        result = self.manager._use_fallback_or_cached("test_resource", {})
        
        # Should return cached data
        self.assertEqual(cached_data, result)
    
    def test_needs_update(self):
        # Set a mock last download time (24 hours ago + 1 second)
        self.manager.last_download_time = {
            "recent_resource": int(time.time()),
            "old_resource": int(time.time()) - (24 * 3600 + 1)
        }
        
        # Test resource that doesn't need updating
        self.assertFalse(self.manager.needs_update("recent_resource"))
        
        # Test resource that needs updating
        self.assertTrue(self.manager.needs_update("old_resource"))
        
        # Test resource that doesn't exist
        self.assertTrue(self.manager.needs_update("nonexistent_resource"))
    
    def test_load_nonexistent_resource(self):
        # Try to load a resource that doesn't exist
        result = self.manager._load_cached_resource("nonexistent")
        self.assertIsNone(result)
    
    def test_load_existing_resource(self):
        # Create a test resource
        test_data = {"key": "value"}
        resource_path = os.path.join(self.temp_dir, "existing_resource.json")
        with open(resource_path, 'w') as f:
            json.dump(test_data, f)
        
        # Load the resource
        result = self.manager._load_cached_resource("existing_resource")
        self.assertEqual(test_data, result)


if __name__ == '__main__':
    unittest.main()