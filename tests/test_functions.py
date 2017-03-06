import unittest

import numpy as np

from brainforge.ops import act_fns
from csxdata import etalon


class TestSoftmax(unittest.TestCase):

    def setUp(self):
        self.data = etalon()
        self.softmax = act_fns["softmax"]()
        self.rsmaxed = np.round(etalon("smaxed.csv").learning.astype(float), 4)

    def test_softmax_function(self):

        output = self.softmax(self.data.learning)
        output = np.round(output.astype(float), 4)

        self.assertTrue(np.allclose(output, self.rsmaxed))

if __name__ == '__main__':
    unittest.main()
