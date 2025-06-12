import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.search import add_to_index, remove_from_index, query_index


class MockModel:
    """Mock model class for testing search functions"""
    __searchable__ = ['field1', 'field2']
    
    def __init__(self, id=1, field1='Test Content', field2='More Content'):
        self.id = id
        self.field1 = field1
        self.field2 = field2


class SearchTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.elasticsearch = MagicMock()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create mock model
        self.model = MockModel()
        
    def tearDown(self):
        self.app_context.pop()
        
    def test_add_to_index(self):
        """Test adding a document to the search index"""
        # Call function
        add_to_index('test_index', self.model)
        
        # Verify elasticsearch was called correctly
        self.app.elasticsearch.index.assert_called_once_with(
            index='test_index',
            id=self.model.id,
            document={
                'field1': 'Test Content',
                'field2': 'More Content'
            }
        )
    
    def test_add_to_index_no_elasticsearch(self):
        """Test adding a document when elasticsearch is not configured"""
        # Set elasticsearch to None temporarily
        self.app.elasticsearch = None
        
        # Should not raise an exception
        add_to_index('test_index', self.model)
        
        # Restore elasticsearch for other tests
        self.app.elasticsearch = MagicMock()
    
    def test_remove_from_index(self):
        """Test removing a document from the search index"""
        # Call function
        remove_from_index('test_index', self.model)
        
        # Verify elasticsearch delete was called correctly
        self.app.elasticsearch.delete.assert_called_once_with(
            index='test_index',
            id=self.model.id
        )
    
    def test_remove_from_index_no_elasticsearch(self):
        """Test removing a document when elasticsearch is not configured"""
        # Set elasticsearch to None temporarily
        self.app.elasticsearch = None
        
        # Should not raise an exception
        remove_from_index('test_index', self.model)
        
        # Restore elasticsearch for other tests
        self.app.elasticsearch = MagicMock()
    
    def test_query_index(self):
        """Test searching the index"""
        # Setup mock response
        mock_search_result = {
            'hits': {
                'hits': [
                    {'_id': '1'},
                    {'_id': '2'}
                ],
                'total': {'value': 2}
            }
        }
        self.app.elasticsearch.search.return_value = mock_search_result
        
        # Call function
        ids, total = query_index('test_index', 'test query', 1, 10)
        
        # Verify elasticsearch search was called correctly
        self.app.elasticsearch.search.assert_called_once_with(
            index='test_index',
            query={'multi_match': {'query': 'test query', 'fields': ['*']}},
            from_=0,  # (1-1) * 10
            size=10
        )
        
        # Verify results
        self.assertEqual(ids, [1, 2])
        self.assertEqual(total, 2)
    
    def test_query_index_pagination(self):
        """Test search pagination"""
        # Setup mock response
        mock_search_result = {
            'hits': {
                'hits': [
                    {'_id': '3'},
                    {'_id': '4'}
                ],
                'total': {'value': 10}  # Total of 10 results
            }
        }
        self.app.elasticsearch.search.return_value = mock_search_result
        
        # Call function with page 2, 2 per page
        ids, total = query_index('test_index', 'test query', 2, 2)
        
        # Verify elasticsearch search was called with correct pagination
        self.app.elasticsearch.search.assert_called_once_with(
            index='test_index',
            query={'multi_match': {'query': 'test query', 'fields': ['*']}},
            from_=2,  # (2-1) * 2
            size=2
        )
        
        # Verify results
        self.assertEqual(ids, [3, 4])
        self.assertEqual(total, 10)
    
    def test_query_index_no_elasticsearch(self):
        """Test search when elasticsearch is not configured"""
        # Set elasticsearch to None temporarily
        self.app.elasticsearch = None
        
        # Call function
        ids, total = query_index('test_index', 'test query', 1, 10)
        
        # Verify empty results
        self.assertEqual(ids, [])
        self.assertEqual(total, 0)


if __name__ == '__main__':
    unittest.main()
