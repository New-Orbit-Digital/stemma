#!/usr/bin/env python3
"""Run the Stemma test suite: stdlib unittest discovery over tests/.

The one way to run the suite. Prints the totals and exits nonzero on any
failure or error.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(ROOT, "tests")


def main():
    if not os.path.isdir(TESTS):
        print("error: %s is not a directory" % TESTS)
        return 1
    suite = unittest.TestLoader().discover(start_dir=TESTS, pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(
        "%d tests, %d failures, %d errors, %d skipped"
        % (
            result.testsRun,
            len(result.failures),
            len(result.errors),
            len(result.skipped),
        )
    )
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
