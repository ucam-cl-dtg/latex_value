#!/usr/bin/env python3

import unittest
from latex_value import display_num

class TestDisplayNum(unittest.TestCase):
    def test_small(self):
        cases = [(0,'0'),(-1,'-1'),(1,'1'), (137.0, '137'), (1234, r'1\,230'),
        	(10010101, r'10\,000\,000'), (12.3, '12.3'), (-12.3, '-12.3')]
        for test_case, result in cases:
            self.assertEqual(display_num(test_case), result)

if __name__ == '__main__':
    unittest.main()
