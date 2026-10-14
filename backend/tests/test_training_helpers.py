import unittest
import pandas as pd
from train import encode_target, norm, EXCLUDED_NORMALIZED

class TrainingHelperTests(unittest.TestCase):
    def test_cad_label_mapping(self):
        self.assertEqual(encode_target(pd.Series(['Cad', 'Normal'])).tolist(), [1, 0])

    def test_stenosis_label_mapping(self):
        self.assertEqual(encode_target(pd.Series(['Stenotic', 'Normal'])).tolist(), [1, 0])

    def test_target_columns_are_excluded(self):
        for name in ['Cath', 'CAD', 'LAD', 'LCX', 'RCA']:
            self.assertIn(norm(name), EXCLUDED_NORMALIZED)

    def test_unknown_labels_fail_loudly(self):
        with self.assertRaises(ValueError):
            encode_target(pd.Series(['Maybe', 'Normal']))

if __name__ == '__main__':
    unittest.main()
