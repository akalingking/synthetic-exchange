import logging
import unittest as ut
from test.test_agents import AgentsTest
from test.test_market import MarketTest


def main():
    loader = ut.TestLoader()
    tests = [
        loader.loadTestsFromTestCase(test)
        for test in [
            # AgentsTest,
            MarketTest,
        ]
    ]
    suite = ut.TestSuite(tests)
    runner = ut.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()