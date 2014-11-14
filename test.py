#!/usr/bin/env python3

import unittest
from latex_value import display_num
from uncertainties import ufloat

class TestDisplayNum(unittest.TestCase):
    def test_small(self):
        cases = [(0,'0'),(-1,'-1'),(1,'1'), (137.0, '137'), (1234, r'1\,230'),
        	(10010101, r'10\,000\,000'), (12.3, '12.3'), (-12.3, '-12.3')]
        for test_case, result in cases:
            self.assertEqual(display_num(test_case), result)

    def test_small(self):
        cases = [(ufloat(0,0), r'0.0 \pm 0.0'), (ufloat(10,0), r'10.0 \pm 0.0')
                , (ufloat(10.0,0.1), r'10.0 \pm 0.1'), (ufloat(100.0,0.1), r'100 \pm 0')]
        for test_case, result in cases:
            self.assertEqual(display_num(test_case), result)


if __name__ == '__main__':
    unittest.main()
