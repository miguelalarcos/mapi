import unittest
from unittest.mock import MagicMock, patch
from schema import Schema, public, never, read_only, \
     SetError, ValidationError, PathError, is_owner, required, private, current_user_is


class TestGetMethods(unittest.TestCase):

    def test_schema_simple_get(self):
        schema_plain = {
            'a': {
                'type': int,
                'get': public
            }
        }

        A = Schema(schema_plain)

        value = A.get( {'a': 3})    
        self.assertEqual(value, {'a': 3})        

    def test_schema_simple_get_forbidden(self):
        schema_plain = {
            'a': {
                'type': int,
                'get': private
            }
        }

        A = Schema(schema_plain)

        value = A.get( {'a': 3})    
        self.assertEqual(value, {})        

    def test_schema_path_get(self):
        schema_plain = {
            'b': {
                'type': str,
                'get': public
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            'a': {
                'type': B,
                'set': public
            }
        }

        A = Schema(schema_plain)

        value = A.get({'a': {'b': 'hello'}})    
        self.assertEqual(value, {'a': {'b': 'hello'}})

    def test_schema_path_b_is_private(self):
        schema_plain = {
            'b': {
                'type': str,
                'get': private
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            'a': {
                'type': B,
                'set': public
            }
        }

        A = Schema(schema_plain)

        value = A.get({'a': {'b': 'hello'}})    
        self.assertEqual(value, {'a': {}})

    def test_schema_path_b_is_not_owner(self):
        schema_plain = {
            'b': {
                'type': str,
                'get': is_owner
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            'a': {
                'type': B,
                'set': public
            }
        }

        A = Schema(schema_plain)

        with patch('schema.current_user') as mock:
            mock.return_value = 'miguel'
            value = A.get({'__owners': ['miguel.'], 'a': {'b': 'hello'}})    
            self.assertEqual(value, {'a': {}})

    def test_schema_path_b_is_owner(self):
        schema_plain = {
            'b': {
                'type': str,
                'get': is_owner
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            'a': {
                'type': B,
                'set': public
            }
        }

        A = Schema(schema_plain)

        with patch('schema.current_user') as mock:
            mock.return_value = 'miguel'
            value = A.get({'__owners': ['miguel'], 'a': {'b': 'hello'}})    
            self.assertEqual(value, {'a': {'b': 'hello'}})

    def test_schema_path_b_is_not_current_user_miguel(self):
        schema_plain = {
            'b': {
                'type': str,
                'get': current_user_is('user')
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            'a': {
                'type': B,
                'set': public
            },
            'user': {
                'type': str
            }
        }

        A = Schema(schema_plain)

        with patch('schema.current_user') as mock:
            mock.return_value = 'miguelxxx'
            value = A.get({'user': 'miguel', 'a': {'b': 'hello'}})    
            self.assertEqual(value, {'user': 'miguel', 'a': {}})

    def test_schema_path_b_is_current_user_miguel(self):
        schema_plain = {
            'b': {
                'type': str,
                'get': current_user_is('user')
            }
        }
        B = Schema(schema_plain)
        
        schema_plain = {
            'a': {
                'type': B,
                'set': public
            },
            'user': {
                'type': str
            }
        }

        A = Schema(schema_plain)

        with patch('schema.current_user') as mock:
            mock.return_value = 'miguel'
            value = A.get({'user': 'miguel', 'a': {'b': 'hello'}})    
            self.assertEqual(value, {'user': 'miguel', 'a': {'b': 'hello'}})

class TestPostMethods(unittest.TestCase):

    def test_schema_simple_post(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': int,
                'set': public
            }
        }

        A = Schema(schema_plain)

        value = A.post( {'a': 3})    
        self.assertEqual(value, {'a': 3})        

    def test_schema_simple_post_with_initial(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': int,
                'set': public,
                'initial': lambda ctx: 7
            }
        }

        A = Schema(schema_plain)

        value = A.post({})    
        self.assertEqual(value, {'a': 7})        

    def test_schema_simple_post_computed(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': int,
                'set': read_only,
                'computed': lambda x: 5
            }
        }

        A = Schema(schema_plain)

        value = A.post( {})    
        self.assertEqual(value, {'a': 5}) 

    def test_schema_simple_post_required(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': int,
                'set': public,
                'validation': lambda x: required(x)
            }
        }

        A = Schema(schema_plain)

        value = A.post( {'a': 3})    
        self.assertEqual(value, {'a': 3}) 


    def test_schema_simple_post_required_forbidden(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': int,
                'set': public,
                'validation': lambda x: required(x)
            }
        }

        A = Schema(schema_plain)

        with self.assertRaises(ValidationError):
            value = A.post({})    

    def test_schema_path_post(self):
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

        value = A.post({'a': {'b': 'hello'}})    
        self.assertEqual(value, {'a': {'b': 'hello'}})

    def test_schema_path_post_forbidden(self):
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

        with self.assertRaises(ValidationError):
            value = A.post({'a': {'b': 5}}) 
           
    def test_schema_path_post_forbidden_validation(self):
        schema_plain = {
            'b': {
                'type': int,
                'set': public,
                'validation': lambda x: x > 5
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

        with self.assertRaises(ValidationError):
            value = A.post({'a': {'b': 5}})         


class TestPutMethods(unittest.TestCase):

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

    def test_schema_simple_set_read_only(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': int,
                'set': read_only
            }
        }

        A = Schema(schema_plain)

        with self.assertRaises(SetError):
            value = A.put('a', {}, 5)    

    def test_schema_simple_set_computed(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': int,
                'set': public,
                'computed': lambda x: 5
            }
        }

        A = Schema(schema_plain)

        value = A.put('a', {}, 3)    
        self.assertEqual(value, 5)

    def test_schema_simple_is_owner(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': is_owner,
            'a': {
                'type': int
            }
        }

        A = Schema(schema_plain)
        with patch('schema.current_user') as mock:
            mock.return_value = 'miguel'
            value = A.put('a', {'__owners': 'miguel'}, 5)    
            self.assertEqual(value, 5)

    def test_schema_simple_set_with_already_data(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': never,
            'a': {
                'type': int,
                'set': public
            }
        }

        A = Schema(schema_plain)

        value = A.put('a', {'a': 0}, 5)    
        self.assertEqual(value, 5)

    def test_schema_simple_set_forbidden_by_type(self):
        schema_plain = {
            '__set_document': public, 
            '__set_default': public,
            'a': {
                'type': int
            }
        }

        A = Schema(schema_plain)

        with self.assertRaises(ValidationError):
            A.put('a', {}, '5') 

    def test_schema_simple_set_forbidden_never(self):
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

    def test_schema_simple_set_forbidden_by_validation(self):
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

    def test_schema_path_set_computed(self):
        schema_plain = {
            'b': {
                'type': str,
                'set': public,
                'computed': lambda x: 'insert coin'
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
        self.assertEqual(value, 'insert coin')

    def test_schema_path_set_is_owner(self):
        schema_plain = {
            'b': {
                'type': str,
                'set': is_owner
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

        with patch('schema.current_user') as mock:
            mock.return_value = 'miguel'
            value = A.put('a.b', {'__owners': 'miguel', 'a': {}}, 'hello :)')    
            self.assertEqual(value, 'hello :)')

    def test_schema_path_set_is_owner_array(self):
        schema_plain = {
            'b': {
                'type': str,
                'set': is_owner
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

        with patch('schema.current_user') as mock:
            mock.return_value = 'miguel'
            value = A.put('a.0.b', {'__owners': 'miguel', 'a': [{'b': 'insert coin'}]}, 'hello :)')    
            self.assertEqual(value, 'hello :)')

    def test_schema_path_set_is_owner_array_0_index(self):
        schema_plain = {
            'b': {
                'type': str,
                'set': is_owner
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

        with patch('schema.current_user') as mock:
            mock.return_value = 'miguel'
            value = A.put('a.0', {'__owners': 'miguel', 'a': [{'b': 'insert coin'}]}, {'b': 'hello :)'})    
            self.assertEqual(value, {'b': 'hello :)'})

    def test_schema_path_set_path_does_not_exist(self):
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

        with self.assertRaises(PathError):
            value = A.put('a.b', {}, 'hello :)')    

    def test_schema_path_set_object(self):
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

        value = A.put('a', {}, {'b': 'hello :)'})    
        self.assertEqual(value, {'b': 'hello :)'})

    def test_schema_path_set_object_array(self):
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

        value = A.put('a', {}, {'b': 'hello :)'})    
        self.assertEqual(value, {'b': 'hello :)'})

    def test_schema_path_set_object_array_invalid_type(self):
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

        with self.assertRaises(PathError):
            value = A.put('a', {}, 1)    
        
    def test_schema_path_set_object_array_invalid_type2(self):
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

        with self.assertRaises(PathError):
            value = A.put('a', {}, {})  

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

    def test_schema_path_set_object_array_valid_current_user_is(self):
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
                'set': current_user_is('user')
            }
        }

        A = Schema(schema_plain)

        with patch('schema.current_user') as mock:
            mock.return_value = 'miguel'
            value = A.put('a', {'user': 'miguel'}, {'b': 'hello :)'})    
            self.assertEqual(value, {'b': 'hello :)'})

    def test_schema_path_set_object_array_invalid_current_user_is(self):
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
                'set': current_user_is('user')
            }
        }

        A = Schema(schema_plain)

        with patch('schema.current_user') as mock:
            mock.return_value = 'miguel'
            with self.assertRaises(SetError):
                A.put('a', {'user': 'miguelxxx'}, {'b': 'hello :)'})   

if __name__ == '__main__':
    unittest.main()