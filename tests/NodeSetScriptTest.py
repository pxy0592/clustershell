#!/usr/bin/env python
# scripts/nodeset.py tool test suite 
# Written by S. Thiell 2009-07-29
# $Id$


"""Unit test for scripts/nodeset.py"""

import copy
import sys
import unittest

from subprocess import *


class NodeSetScriptTest(unittest.TestCase):
    """Unit test class for testing nodeset.py"""

    def _launchAndCompare(self, args, expected_output):
        output = Popen(["../scripts/nodeset.py"] + args, stdout=PIPE).communicate()[0].strip()
        if type(expected_output) is list:
            ok = False
            for o in expected_output:
                if output == o:
                    ok = True
            self.assert_(ok, "Output %s != one of %s" % (output, expected_output))
        else:
            self.assertEqual(expected_output, output)

    def _launchBatteryOfCountTests(self, args):
        self._launchAndCompare(args + ["--count", "foo"], "1")
        self._launchAndCompare(args + ["--count", "foo", "bar"], "2")
        self._launchAndCompare(args + ["--count", "foo", "foo"], "1")
        self._launchAndCompare(args + ["--count", "foo", "foo", "bar"], "2")
        self._launchAndCompare(args + ["--count", "foo[0]"], "1")
        self._launchAndCompare(args + ["--count", "foo[2]"], "1")
        self._launchAndCompare(args + ["--count", "foo[1,2]"], "2")
        self._launchAndCompare(args + ["--count", "foo[1-2]"], "2")
        self._launchAndCompare(args + ["--count", "foo[1,2]", "foo[1-2]"], "2")
        self._launchAndCompare(args + ["--count", "foo[1-200,245-394]"], "350")
        self._launchAndCompare(args + ["--count", "foo[395-442]", "foo[1-200,245-394]"], "398")
        self._launchAndCompare(args + ["--count", "foo[395-442]", "foo", "foo[1-200,245-394]"], "399")
        self._launchAndCompare(args + ["--count", "foo[395-442]", "foo", "foo[0-200,245-394]"], "400")
        self._launchAndCompare(args + ["--count", "foo[395-442]", "bar3,bar24", "foo[1-200,245-394]"], "400")

    def testCount(self):
        """test nodeset.py --count"""
        self._launchBatteryOfCountTests([])
        self._launchBatteryOfCountTests(["--autostep=1"])
        self._launchBatteryOfCountTests(["--autostep=2"])
        self._launchBatteryOfCountTests(["--autostep=5"])

    def testCountIntersection(self):
        """test nodeset.py --count --intersection"""
        self._launchAndCompare(["--count", "--intersection", "foo"], "1")
        self._launchAndCompare(["--count", "--intersection", "foo", "bar"], "0")
        self._launchAndCompare(["--count", "--intersection", "foo", "foo"], "1")
        self._launchAndCompare(["--count", "--intersection", "foo", "foo", "bar"], "0")
        self._launchAndCompare(["--count", "--intersection", "foo[0]"], "1")
        self._launchAndCompare(["--count", "--intersection", "foo[2]"], "1")
        self._launchAndCompare(["--count", "--intersection", "foo[1,2]"], "2")
        self._launchAndCompare(["--count", "--intersection", "foo[1-2]"], "2")
        self._launchAndCompare(["--count", "--intersection", "foo[1,2]", "foo[1-2]"], "2")
        self._launchAndCompare(["--count", "--intersection", "foo[1-200,245-394]"], "350")
        self._launchAndCompare(["--count", "--intersection", "foo[395-442]", "foo[1-200,245-394]"], "0")
        self._launchAndCompare(["--count", "--intersection", "foo[395-442]", "foo", "foo[1-200,245-394]"], "0")
        self._launchAndCompare(["--count", "--intersection", "foo[395-442]", "foo", "foo[0-200,245-394]"], "0")
        self._launchAndCompare(["--count", "--intersection", "foo[395-442]", "bar3,bar24", "foo[1-200,245-394]"], "0")

    def _launchBatteryOfFoldTests(self, args):
        self._launchAndCompare(args + ["--fold", "foo"], "foo")
        self._launchAndCompare(args + ["--fold", "foo", "bar"], ["bar,foo", "foo,bar"])
        self._launchAndCompare(args + ["--fold", "foo", "foo"], "foo")
        self._launchAndCompare(args + ["--fold", "foo", "foo", "bar"], ["bar,foo", "foo,bar"])
        self._launchAndCompare(args + ["--fold", "foo[0]"], "foo0")
        self._launchAndCompare(args + ["--fold", "foo[2]"], "foo2")
        self._launchAndCompare(args + ["--fold", "foo[1,2]"], "foo[1-2]")
        self._launchAndCompare(args + ["--fold", "foo[1-2]"], "foo[1-2]")
        self._launchAndCompare(args + ["--fold", "foo[1,2]", "foo[1-2]"], "foo[1-2]")
        self._launchAndCompare(args + ["--fold", "foo[1-200,245-394]"], "foo[1-200,245-394]")
        self._launchAndCompare(args + ["--fold", "foo[395-442]", "foo[1-200,245-394]"], "foo[1-200,245-442]")
        self._launchAndCompare(args + ["--fold", "foo[395-442]", "foo", "foo[1-200,245-394]"], ["foo[1-200,245-442],foo", "foo,foo[1-200,245-442],foo"])
        self._launchAndCompare(args + ["--fold", "foo[395-442]", "foo", "foo[0-200,245-394]"], ["foo[0-200,245-442],foo", "foo,foo[0-200,245-442]"])
        self._launchAndCompare(args + ["--fold", "foo[395-442]", "bar3,bar24", "foo[1-200,245-394]"], ["foo[1-200,245-442],bar[3,24]", "bar[3,24],foo[1-200,245-442]"])

    def testFold(self):
        """test nodeset.py --fold"""
        self._launchBatteryOfFoldTests([])
        self._launchBatteryOfFoldTests(["--autostep=3"])

    def testExpand(self):
        """test nodeset.py --expand"""
        self._launchAndCompare(["--expand", "foo"], "foo")
        self._launchAndCompare(["--expand", "foo", "bar"], ["bar foo", "foo bar"])
        self._launchAndCompare(["--expand", "foo", "foo"], "foo")
        self._launchAndCompare(["--expand", "foo[0]"], "foo0")
        self._launchAndCompare(["--expand", "foo[2]"], "foo2")
        self._launchAndCompare(["--expand", "foo[1,2]"], "foo1 foo2")
        self._launchAndCompare(["--expand", "foo[1-2]"], "foo1 foo2")
        self._launchAndCompare(["--expand", "foo[1-2],bar"], ["bar foo1 foo2", "foo1 foo2 bar"])

    def testFoldXOR(self):
        """test nodeset.py --fold --xor"""
        self._launchAndCompare(["-X", "--fold", "foo"], "foo")
        self._launchAndCompare(["-X", "--fold", "foo", "bar"], ["bar,foo", "foo,bar"])
        self._launchAndCompare(["-X", "--fold", "foo", "foo"], "")
        self._launchAndCompare(["-X", "--fold", "foo", "foo", "bar"], "bar")
        self._launchAndCompare(["-X", "--fold", "foo[0]"], "foo0")
        self._launchAndCompare(["-X", "--fold", "foo[2]"], "foo2")
        self._launchAndCompare(["-X", "--fold", "foo[1,2]"], "foo[1-2]")
        self._launchAndCompare(["-X", "--fold", "foo[1-2]"], "foo[1-2]")
        self._launchAndCompare(["-X", "--fold", "foo[1,2]", "foo[1-2]"], "")
        self._launchAndCompare(["-X", "--fold", "foo[1-10]", "foo[5-15]"], "foo[1-4,11-15]")
        self._launchAndCompare(["-X", "--fold", "foo[1-200,245-394]"], "foo[1-200,245-394]")
        self._launchAndCompare(["-X", "--fold", "foo[395-442]", "foo[1-200,245-394]"], "foo[1-200,245-442]")
        self._launchAndCompare(["-X", "--fold", "foo[395-442]", "foo", "foo[1-200,245-394]"], ["foo[1-200,245-442],foo", "foo,foo[1-200,245-442],foo"])
        self._launchAndCompare(["-X", "--fold", "foo[395-442]", "foo", "foo[0-200,245-394]"], ["foo[0-200,245-442],foo", "foo,foo[0-200,245-442]"])
        self._launchAndCompare(["-X", "--fold", "foo[395-442]", "bar3,bar24", "foo[1-200,245-394]"], ["foo[1-200,245-442],bar[3,24]", "bar[3,24],foo[1-200,245-442]"])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(NodeSetScriptTest)
    unittest.TextTestRunner(verbosity=2).run(suite)