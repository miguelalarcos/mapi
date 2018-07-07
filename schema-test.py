import unittest
from unittest.mock import MagicMock
from schema import Schema, public, never, read_only, SetError, ValidationError

is_owner = MagicMock(return_value=False)

class TestSetMethods(unittest.TestCase):

    def test_schema_simple_set(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': int,
                'set': public
            }
        }

        A = Schema(schema_plain)

        value = A.put('a', {}, 5)    
        self.assertEqual(value, 5)

    def test_schema_simple_set_forbidden(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': int
            }
        }

        A = Schema(schema_plain)

        with self.assertRaises(SetError):
            A.put('a', {'a': 7}, 5)    

    def test_schema_simple_set_forbidden_2(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': public,
            'a': {
                'type': int,
                'validation': lambda x: x > 5
            }
        }

        A = Schema(schema_plain)

        with self.assertRaises(ValidationError):
            A.put('a', {'a': 7}, 5) 

    def test_schema_path_set(self):
        schema_plain = {
            'b': {
                'type': str,
                'set': public
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': B,
                'set': public
            }
        }

        A = Schema(schema_plain)

        value = A.put('a.b', {'a': {}}, 'hello :)')    
        self.assertEqual(value, 'hello :)')

    def test_schema_path_set_forbidden_read_only(self):
        schema_plain = {
            'b': {
                'type': str,
                'set': public
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': B,
                'set': read_only
            }
        }

        A = Schema(schema_plain)

        with self.assertRaises(SetError):
            A.put('a.b', {'a': {}}, {'b': 'hello :)'})    

    def test_schema_path_array_set_forbidden_array_read_only(self):
        schema_plain = {
            'b': {
                'type': str,
                'set': public
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': [B],
                'set': read_only
            }
        }

        A = Schema(schema_plain)

        with self.assertRaises(SetError):
            A.put('a.0.b', {'a': [{'b': 'game over!'}]}, {'b': 'hello :)'})    
        
    def test_schema_path_array_set_forbidden_array_inside_read_only(self):
        schema_plain = {
            'b': {
                'type': str,
                'set': read_only
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': [B],
                'set': public
            }
        }

        A = Schema(schema_plain)

        with self.assertRaises(SetError):
            A.put('a.0.b', {'a': [{'b': 'game over!'}]}, {'b': 'hello :)'})    

    def test_schema_path_array_nested_set(self):
        schema_plain = {
            'b': {
                'type': str,
                'set': public
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': [B],
                'set': public
            }
        }

        A = Schema(schema_plain)

        value = A.put('a.0.b', {'a': [{'b': 'insert coin'}]}, 'hello :)')    
        self.assertEqual(value, 'hello :)')

if __name__ == '__main__':
    unittest.main()