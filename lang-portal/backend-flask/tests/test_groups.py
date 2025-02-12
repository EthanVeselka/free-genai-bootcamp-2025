import unittest
from flask import Flask
from routes.groups import load as load_groups

class TestGroupsRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Mock the database cursor
        class MockDB:
            def cursor(self):
                return MockCursor()
            def commit(self):
                pass
            def close(self):
                pass
            
        class MockCursor:
            def __init__(self):
                self.last_query = None
                self.last_params = None
                
            def execute(self, query, params=None):
                self.last_query = query
                self.last_params = params
                
            def fetchone(self):
                if "SELECT name FROM groups" in self.last_query:
                    # Check params instead of SQL string
                    if self.last_params and self.last_params[0] == 1:
                        return {"name": "Test Group"}
                    return None
                return None
                
            def fetchall(self):
                if "SELECT w.*" in self.last_query:
                    # Check params instead of SQL string
                    if self.last_params and self.last_params[0] == 1:
                        return [
                            {
                                "id": 1,
                                "kanji": "日本語",
                                "romaji": "nihongo",
                                "english": "Japanese language"
                            },
                            {
                                "id": 2,
                                "kanji": "漢字",
                                "romaji": "kanji",
                                "english": "Chinese characters"
                            }
                        ]
                return []
                
        self.app.db = MockDB()
        load_groups(self.app)
        self.client = self.app.test_client()

    def test_get_group_words_raw(self):
        # Test getting raw words for a valid group
        response = self.client.get('/groups/1/words/raw')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Check response structure
        self.assertTrue(isinstance(data, list))
        self.assertEqual(len(data), 2)
        
        # Check first word
        self.assertEqual(data[0]['id'], 1)
        self.assertEqual(data[0]['kanji'], "日本語")
        self.assertEqual(data[0]['romaji'], "nihongo")
        self.assertEqual(data[0]['english'], "Japanese language")
        
        # Test with non-existent group
        response = self.client.get('/groups/999/words/raw')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], "Group not found")

if __name__ == '__main__':
    unittest.main() 