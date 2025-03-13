"""
Test runner module for Tumkwe Invest.
"""

import unittest
import os
import sys
from pathlib import Path


class IntegrationTestRunner(unittest.TextTestRunner):
    """
    Custom test runner that allows for integration tests to be run only when specified.
    
    Set the environment variable RUN_INTEGRATION_TESTS=1 to run integration tests.
    """
    
    def run(self, test):
        """
        Run the test suite, skipping integration tests if not explicitly enabled.
        """
        run_integration = os.environ.get("RUN_INTEGRATION_TESTS") == "1"
        
        # Mark integration tests to skip if not running integration tests
        if not run_integration:
            for test_case in test:
                if isinstance(test_case, unittest.TestCase):
                    if "Integration" in test_case.__class__.__name__:
                        setattr(test_case, "setUp", lambda: test_case.skipTest("Integration tests disabled"))
                else:
                    # Handle test suites
                    for sub_test in test_case:
                        if isinstance(sub_test, unittest.TestCase):
                            if "Integration" in sub_test.__class__.__name__:
                                setattr(sub_test, "setUp", lambda: sub_test.skipTest("Integration tests disabled"))
                                
        return super().run(test)


def run_all_tests():
    """
    Run all tests in the project.
    """
    # Find test directory
    test_dir = Path(__file__).parent
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir))
    
    # Run tests with custom runner
    runner = IntegrationTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    run_all_tests()
