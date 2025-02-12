import unittest
from flask import Flask
from routes.study_sessions import load as load_study_sessions

class TestStudySessionsRoutes(unittest.TestCase):
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
            def rollback(self):
                pass
            
        class MockCursor:
            def __init__(self):
                self.last_query = None
                
            def execute(self, query, params=None):
                self.last_query = query
                
            def fetchone(self):
                if self.last_query and "SELECT" in self.last_query:
                    return {
                        'id': 1,
                        'group_id': 1,
                        'group_name': 'Test Group',
                        'activity_id': 1,
                        'activity_name': 'Test Activity',
                        'created_at': '2024-01-01 00:00:00'
                    }
                return None
                
            def lastrowid(self):
                return 1
                
        self.app.db = MockDB()
        load_study_sessions(self.app)
        self.client = self.app.test_client()

    def test_create_study_session(self):
        # Test creating a new study session
        response = self.client.post('/api/study-sessions', 
                                  json={
                                      'group_id': 1,
                                      'study_activity_id': 1
                                  })
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['group_id'], 1)
        self.assertEqual(data['activity_id'], 1)
        self.assertIn('start_time', data)

    def test_submit_session_review(self):
        # Test submitting a review for a session
        response = self.client.post('/api/study-sessions/1/review',
                                  json={
                                      'word_id': 1,
                                      'correct': True
                                  })
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['message'], 'Review submitted successfully')

if __name__ == '__main__':
    unittest.main() 