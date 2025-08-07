#!/usr/bin/env python3
"""
Test runner for Nord Stern Car Numbers application
"""

import unittest
import sys
import os
import argparse
from pathlib import Path


def run_tests(test_pattern=None, verbose=False, coverage=False):
    """Run the test suite"""

    # Add the project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    # Discover and run tests
    loader = unittest.TestLoader()

    if test_pattern:
        # Run specific test pattern
        suite = loader.loadTestsFromName(test_pattern)
    else:
        # Discover all tests
        suite = loader.discover("tests", pattern="test_*.py")

    # Configure test runner
    if verbose:
        verbosity = 2
    else:
        verbosity = 1

    # Run tests with coverage if requested
    if coverage:
        try:
            import coverage

            cov = coverage.Coverage()
            cov.start()

            runner = unittest.TextTestRunner(verbosity=verbosity)
            result = runner.run(suite)

            cov.stop()
            cov.save()

            print("\n" + "=" * 60)
            print("COVERAGE REPORT")
            print("=" * 60)
            cov.report()

            # Generate HTML report
            cov.html_report(directory="htmlcov")
            print(f"\nHTML coverage report generated in: htmlcov/")

            return result.wasSuccessful()

        except ImportError:
            print(
                "Warning: coverage package not installed. Install with: pip install coverage"
            )
            print("Running tests without coverage...")
            coverage = False

    if not coverage:
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        return result.wasSuccessful()


def main():
    """Main function to parse arguments and run tests"""
    parser = argparse.ArgumentParser(description="Run Nord Stern Car Numbers tests")
    parser.add_argument(
        "--pattern",
        "-p",
        help="Test pattern to run (e.g., tests.test_app.NordSternCarNumbersTestCase.test_home_page)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Run with coverage report"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="List all available tests"
    )

    args = parser.parse_args()

    if args.list:
        # List all available tests
        loader = unittest.TestLoader()
        suite = loader.discover("tests", pattern="test_*.py")

        print("Available tests:")
        print("=" * 50)

        for test_case in suite:
            for test_suite in test_case:
                for test in test_suite:
                    print(f"  {test}")

        return

    # Run tests
    success = run_tests(
        test_pattern=args.pattern, verbose=args.verbose, coverage=args.coverage
    )

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
