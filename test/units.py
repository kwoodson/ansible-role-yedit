#!/usr/bin/env python2
'''
 Unit tests for yedit
'''

import unittest
import os

# Removing invalid variable names for tests so that I can
# keep them brief
# pylint: disable=invalid-name,no-name-in-module
# Disable import-error b/c our libraries aren't loaded in jenkins
# pylint: disable=import-error
from yedit import Yedit

# pylint: disable=too-many-public-methods
# Silly pylint, moar tests!
class YeditTest(unittest.TestCase):
    '''
     Test class for yedit
    '''
    data = {'a': 'a',
            'b': {'c': {'d': [{'e': 'x'}, 'f', 'g']}},
           }

    filename = 'yedit_test.yml'

    def setUp(self):
        ''' setup method will create a file and set to known configuration '''
        yed = Yedit(YeditTest.filename)
        yed.yaml_dict = YeditTest.data
        yed.write()

    def test_load(self):
        ''' Testing a get '''
        yed = Yedit('yedit_test.yml')
        self.assertEqual(yed.yaml_dict, self.data)

    def test_write(self):
        ''' Testing a simple write '''
        yed = Yedit('yedit_test.yml')
        yed.put('key1', 1)
        yed.write()
        self.assertTrue(yed.yaml_dict.has_key('key1'))
        self.assertEqual(yed.yaml_dict['key1'], 1)

    def test_write_x_y_z(self):
        '''Testing a write of multilayer key'''
        yed = Yedit('yedit_test.yml')
        yed.put('x.y.z', 'modified')
        yed.write()
        yed.load()
        self.assertEqual(yed.get('x.y.z'), 'modified')

    def test_delete_a(self):
        '''Testing a simple delete '''
        yed = Yedit('yedit_test.yml')
        yed.delete('a')
        yed.write()
        yed.load()
        self.assertTrue(not yed.yaml_dict.has_key('a'))

    def test_delete_b_c(self):
        '''Testing delete of layered key '''
        yed = Yedit('yedit_test.yml', separator=':')
        yed.delete('b:c')
        yed.write()
        yed.load()
        self.assertTrue(yed.yaml_dict.has_key('b'))
        self.assertFalse(yed.yaml_dict['b'].has_key('c'))

    def test_create(self):
        '''Testing a create '''
        os.unlink(YeditTest.filename)
        yed = Yedit('yedit_test.yml')
        yed.create('foo', 'bar')
        yed.write()
        yed.load()
        self.assertTrue(yed.yaml_dict.has_key('foo'))
        self.assertTrue(yed.yaml_dict['foo'] == 'bar')

    def test_create_content(self):
        '''Testing a create with content '''
        content = {"foo": "bar"}
        yed = Yedit("yedit_test.yml", content)
        yed.write()
        yed.load()
        self.assertTrue(yed.yaml_dict.has_key('foo'))
        self.assertTrue(yed.yaml_dict['foo'], 'bar')

    def test_array_insert(self):
        '''Testing a create with content '''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('b:c:d[0]', 'inject')
        self.assertTrue(yed.get('b:c:d[0]') == 'inject')

    def test_array_insert_first_index(self):
        '''Testing a create with content '''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('b:c:d[0]', 'inject')
        self.assertTrue(yed.get('b:c:d[1]') == 'f')

    def test_array_insert_second_index(self):
        '''Testing a create with content '''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('b:c:d[0]', 'inject')
        self.assertTrue(yed.get('b:c:d[2]') == 'g')

    def test_dict_array_dict_access(self):
        '''Testing a create with content'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('b:c:d[0]', [{'x': {'y': 'inject'}}])
        self.assertTrue(yed.get('b:c:d[0]:[0]:x:y') == 'inject')

    def test_dict_array_dict_replace(self):
        '''Testing multilevel delete'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('b:c:d[0]', [{'x': {'y': 'inject'}}])
        yed.put('b:c:d[0]:[0]:x:y', 'testing')
        self.assertTrue(yed.yaml_dict.has_key('b'))
        self.assertTrue(yed.yaml_dict['b'].has_key('c'))
        self.assertTrue(yed.yaml_dict['b']['c'].has_key('d'))
        self.assertTrue(isinstance(yed.yaml_dict['b']['c']['d'], list))
        self.assertTrue(isinstance(yed.yaml_dict['b']['c']['d'][0], list))
        self.assertTrue(isinstance(yed.yaml_dict['b']['c']['d'][0][0], dict))
        self.assertTrue(yed.yaml_dict['b']['c']['d'][0][0]['x'].has_key('y'))
        self.assertTrue(yed.yaml_dict['b']['c']['d'][0][0]['x']['y'], 'testing')

    def test_dict_array_dict_remove(self):
        '''Testing multilevel delete'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('b:c:d[0]', [{'x': {'y': 'inject'}}])
        yed.delete('b:c:d[0]:[0]:x:y')
        self.assertTrue(yed.yaml_dict.has_key('b'))
        self.assertTrue(yed.yaml_dict['b'].has_key('c'))
        self.assertTrue(yed.yaml_dict['b']['c'].has_key('d'))
        self.assertTrue(isinstance(yed.yaml_dict['b']['c']['d'], list))
        self.assertTrue(isinstance(yed.yaml_dict['b']['c']['d'][0], list))
        self.assertTrue(isinstance(yed.yaml_dict['b']['c']['d'][0][0], dict))
        self.assertFalse(yed.yaml_dict['b']['c']['d'][0][0]['x'].has_key('y'))

    def test_key_exists_in_dict(self):
        '''Testing exist in dict'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('b:c:d[0]', [{'x': {'y': 'inject'}}])
        self.assertTrue(yed.exists('b:c', 'd'))

    def test_key_exists_in_list(self):
        '''Testing exist in list'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('b:c:d[0]', [{'x': {'y': 'inject'}}])
        self.assertTrue(yed.exists('b:c:d', [{'x': {'y': 'inject'}}]))
        self.assertFalse(yed.exists('b:c:d', [{'x': {'y': 'test'}}]))

    def test_update_to_list_with_index(self):
        '''Testing update to list with index'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('x:y:z', [1, 2, 3])
        yed.update('x:y:z', [5, 6], index=2)
        self.assertTrue(yed.get('x:y:z') == [1, 2, [5, 6]])
        self.assertTrue(yed.exists('x:y:z', [5, 6]))
        self.assertFalse(yed.exists('x:y:z', 4))

    def test_update_to_list_with_curr_value(self):
        '''Testing update to list with index'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('x:y:z', [1, 2, 3])
        yed.update('x:y:z', [5, 6], curr_value=3)
        self.assertTrue(yed.get('x:y:z') == [1, 2, [5, 6]])
        self.assertTrue(yed.exists('x:y:z', [5, 6]))
        self.assertFalse(yed.exists('x:y:z', 4))

    def test_update_to_list(self):
        '''Testing update to list'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('x:y:z', [1, 2, 3])
        yed.update('x:y:z', [5, 6])
        self.assertTrue(yed.get('x:y:z') == [1, 2, 3, [5, 6]])
        self.assertTrue(yed.exists('x:y:z', [5, 6]))
        self.assertFalse(yed.exists('x:y:z', 4))

    def test_append_twice_to_list(self):
        '''Testing append to list'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('x:y:z', [1, 2, 3])
        yed.append('x:y:z', [5, 6])
        yed.append('x:y:z', [5, 6])
        self.assertTrue(yed.get('x:y:z') == [1, 2, 3, [5, 6], [5, 6]])
        self.assertTrue(2 == yed.get('x:y:z').count([5, 6]))
        self.assertFalse(yed.exists('x:y:z', 4))

    def test_add_item_to_dict(self):
        '''Testing update to dict'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('x:y:z', {'a': 1, 'b': 2})
        yed.update('x:y:z', {'c': 3, 'd': 4})
        self.assertTrue(yed.get('x:y:z') == {'a': 1, 'b': 2, 'c': 3, 'd': 4})
        self.assertTrue(yed.exists('x:y:z', {'c': 3}))

    def test_first_level_dict_with_none_value(self):
        '''test dict value with none value'''
        yed = Yedit(content={'a': None}, separator=":")
        yed.put('a:b:c', 'test')
        self.assertTrue(yed.get('a:b:c') == 'test')
        self.assertTrue(yed.get('a:b'), {'c': 'test'})

    def test_adding_yaml_variable(self):
        '''test dict value with none value'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('z:y', '{{test}}')
        self.assertTrue(yed.get('z:y') == '{{test}}')

    def test_keys_with_underscore(self):
        '''test dict value with none value'''
        yed = Yedit("yedit_test.yml", separator=':')
        yed.put('z_:y_y', {'test': '{{test}}'})
        self.assertTrue(yed.get('z_:y_y') == {'test': '{{test}}'})


    def test_first_level_array_update(self):
        '''test update on top level array'''
        yed = Yedit(content=[{'a': 1}, {'b': 2}, {'b': 3}], separator=':')
        yed.update('', {'c': 4})
        self.assertTrue({'c': 4} in yed.get(''))

    def test_first_level_array_delete(self):
        '''test remove top level key'''
        yed = Yedit(content=[{'a': 1}, {'b': 2}, {'b': 3}])
        yed.delete('')
        self.assertTrue({'b': 3} not in yed.get(''))

    def test_first_level_array_get(self):
        '''test dict value with none value'''
        yed = Yedit(content=[{'a': 1}, {'b': 2}, {'b': 3}])
        yed.get('')
        self.assertTrue([{'a': 1}, {'b': 2}, {'b': 3}] == yed.yaml_dict)

    def test_pop_list_item(self):
        '''test dict value with none value'''
        yed = Yedit(content=[{'a': 1}, {'b': 2}, {'b': 3}], separator=':')
        yed.pop('', {'b': 2})
        self.assertTrue([{'a': 1}, {'b': 3}] == yed.yaml_dict)

    def test_pop_list_item_2(self):
        '''test dict value with none value'''
        z = range(10)
        yed = Yedit(content=z, separator=':')
        yed.pop('', 5)
        z.pop(5)
        self.assertTrue(z == yed.yaml_dict)

    def test_pop_dict_key(self):
        '''test dict value with none value'''
        yed = Yedit(content={'a': {'b': {'c': 1, 'd': 2}}}, separator='#')
        yed.pop('a#b', 'c')
        self.assertTrue({'a': {'b': {'d': 2}}} == yed.yaml_dict)

    def tearDown(self):
        '''TearDown method'''
        os.unlink(YeditTest.filename)

if __name__ == "__main__":
    unittest.main()
