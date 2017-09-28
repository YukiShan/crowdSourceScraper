import tempfile
import unittest
from compress_repr import compress_repr


class TestSequenceFunctions(unittest.TestCase):

  def setUp(self):
    self.seq = range(10)
  
  def test_sanity(self):
    actual_output_filename = tempfile.NamedTemporaryFile()
    compress_repr(['testdata/input_1.json', 'testdata/input_2.json'], actual_output_filename)
    actual_output = {}
    with open(actual_output_filename, 'r') as f:
      for l in f.readlines():
        actual_output.update(json.loads(l))
    expected_output = {}
    with open('testdata/expected_output.x.json', 'r') as f:
      for l in f.readlines():
        expected_output.update(json.loads(l))
    self.assertEqual(actual_output, expected_output)


if __name__ == '__main__':
    unittest.main()

