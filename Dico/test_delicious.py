import delicious
from urllib2 import urlopen, HTTPError, Request
import pickle, re, unittest

#class TestDelicious(unittest.TestCase):
#    def test_reader(self):
#        d = delicious.DeliciousAgent()

#        result = d.queryTag("reader")

#        self.assertEqual(result, "http://www.google.com/reader/view/")
