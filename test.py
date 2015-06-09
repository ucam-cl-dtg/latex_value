#!/usr/bin/env python3

import unittest
from latex_value import display_num, find_significance, find_sig_figs_significance
from uncertainties import ufloat

class TestDisplayNum(unittest.TestCase):
    def test_small(self):
        cases = [(0,'0'),(-1,'-1'),(1,'1'), (137.0, '137'), (1234, r'1\,230'),
        	(10010101, r'10\,000\,000'), (12.3, '12.3'), (-12.3, '-12.3')]
        for test_case, result in cases:
            self.assertEqual(display_num(test_case), result)

    def test_ufloat(self):
        cases = [(ufloat(0,0), r'$0.0 \pm 0.0$'), (ufloat(10,0), r'$10.0 \pm 0.0$')
                , (ufloat(10.0,0.1), r'$10.0 \pm 0.1$')
                , (ufloat(100.0,0.1), r'$100 \pm 0$')
                , (ufloat(1.0,1.5e-10), r'$1.0 \pm 0.0$')
                , (ufloat(10.0,0.01), r'$10.0 \pm 0.0$')]
        for test_case, result in cases:
            self.assertEqual(display_num(test_case), result)


class TestFindSigFigsSignificance(unittest.TestCase):
    def test(self):
        cases = [(0.13,0.001), (-1.23, -0.01), (1.3e-10, 1e-12), (13, 0.1), (130000, 1000)]
        for test_case, result in cases:
            self.assertEqual(find_sig_figs_significance(test_case, 3), result)


class TestFindSignificance(unittest.TestCase):
    def test(self):
        cases = [(0.13, 0.01), (-1.23, -0.01), (1.3e-10, 1e-11), (13, 1), (130000, 10000)]
        for test_case, result in cases:
            self.assertEqual(find_significance(test_case, 3), result)


if __name__ == '__main__':
    unittest.main()
