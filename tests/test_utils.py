import collections
from collections.abc import Sequence

from django.contrib.auth.models import User

from controlcenter.utils import captitle, deepmerge, indexonly

from . import TestCase


class SampleTest(TestCase):
    def test_captitle(self):
        title = captitle('TestClass')
        self.assertEqual(title, 'Test class')

    def test_deepmerge(self):
        first = {
            'a': 0,
            'b': {
                'c': {
                    'd': 0,
                    'e': 0
                }
            },
            'f': 0
        }

        second = {
            'a': 1,
            'b': {
                'c': {
                    'd': 1
                }
            },
            'g': 1
        }

        # Just to make sure
        with self.assertRaises(AssertionError):
            self.assertDictEqual(first, second)

        # Merge
        merged = deepmerge(first, second)

        # Checks merged
        self.assertItemsEqual(merged, ['a', 'b', 'f', 'g'])
        self.assertEqual(merged['a'], 1)
        self.assertEqual(merged['b']['c']['d'], 1)
        self.assertEqual(merged['b']['c']['e'], 0)
        self.assertEqual(merged['f'], 0)
        self.assertEqual(merged['g'], 1)

        # First wasn't changed
        self.assertItemsEqual(first, ['a', 'b', 'f'])
        self.assertEqual(first['b']['c']['d'], 0)
        with self.assertRaises(KeyError):
            first['g']

        # Second wasn't changed
        self.assertItemsEqual(second, ['a', 'b', 'g'])
        self.assertEqual(second['b']['c']['d'], 1)
        with self.assertRaises(KeyError):
            second['f']

        # Inner dict check
        with self.assertRaises(KeyError):
            second['b']['c']['e']

    def test_indexonly(self):
        # Built-in types
        self.assertTrue(indexonly(list()))
        self.assertTrue(indexonly(tuple()))
        self.assertFalse(indexonly(dict()))

        # Django model
        self.assertFalse(indexonly(User()))

        class MySequence(Sequence):
            def __init__(self, data):
                self.data = data

            def __getitem__(self, index):
                return self.data[index]

            def __len__(self):
                return len(self.data)

        MyTuple = collections.namedtuple('MyTuple', 'x y')

        # Custom stuff
        self.assertTrue(indexonly(MySequence([0, 1])))
        self.assertFalse(indexonly(MyTuple(0, 1)))
