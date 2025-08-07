#!/usr/bin/env python3
"""
Comprehensive test runner for Nord Stern Car Numbers
Includes code formatting (Black) and linting (flake8) checks
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description, exit_on_failure=True):
    """Run a command and handle the result"""
    print(f"\n🔍 {description}...")
    print(f"   Running: {command}")

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"   ✅ {description} passed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ {description} failed")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            if exit_on_failure:
                print(f"\n💥 Stopping due to {description} failure")
                sys.exit(1)
            return False

    except Exception as e:
        print(f"   ❌ Error running {description}: {e}")
        if exit_on_failure:
            sys.exit(1)
        return False


def check_dependencies():
    """Check if required tools are installed"""
    print("🔧 Checking dependencies...")

    # Check Black
    black_result = subprocess.run("black --version", shell=True, capture_output=True)
    if black_result.returncode != 0:
        print("❌ Black is not installed. Install with: pip install black")
        return False

    # Check flake8
    flake8_result = subprocess.run("flake8 --version", shell=True, capture_output=True)
    if flake8_result.returncode != 0:
        print("❌ flake8 is not installed. Install with: pip install flake8")
        return False

    # Check pytest
    pytest_result = subprocess.run("pytest --version", shell=True, capture_output=True)
    if pytest_result.returncode != 0:
        print("❌ pytest is not installed. Install with: pip install pytest")
        return False

    print("✅ All dependencies are installed")
    return True


def run_quality_checks():
    """Run code quality checks"""
    print("\n🎨 Running Code Quality Checks")
    print("=" * 50)

    # Check Black formatting
    black_success = run_command(
        "black --check --diff .", "Black code formatting check", exit_on_failure=False
    )

    # Run flake8 for critical issues only
    flake8_success = run_command(
        "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
        "Flake8 critical linting check",
        exit_on_failure=False,
    )

    if not black_success:
        print("\n💡 To fix Black formatting issues, run: black .")

    if not flake8_success:
        print(
            "\n💡 To see all flake8 issues, run: flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics"
        )

    return black_success and flake8_success


def run_tests():
    """Run the actual tests"""
    print("\n🧪 Running Tests")
    print("=" * 50)

    # Run tests with verbose output
    test_success = run_command(
        "python -m pytest tests/ -v", "Unit tests", exit_on_failure=True
    )

    return test_success


def run_coverage():
    """Run test coverage"""
    print("\n📊 Running Test Coverage")
    print("=" * 50)

    coverage_success = run_command(
        "python -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html",
        "Test coverage report",
        exit_on_failure=False,
    )

    if coverage_success:
        print("\n📁 Coverage report generated in htmlcov/index.html")

    return coverage_success


def main():
    """Main test runner"""
    print("🚀 Nord Stern Car Numbers - Comprehensive Test Runner")
    print("=" * 60)

    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        sys.exit(1)

    # Run quality checks
    quality_passed = run_quality_checks()

    # Run tests
    tests_passed = run_tests()

    # Run coverage
    coverage_passed = run_coverage()

    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    print(f"   Code Quality: {'✅ PASSED' if quality_passed else '❌ FAILED'}")
    print(f"   Unit Tests:   {'✅ PASSED' if tests_passed else '❌ FAILED'}")
    print(f"   Coverage:     {'✅ PASSED' if coverage_passed else '❌ FAILED'}")

    if quality_passed and tests_passed:
        print("\n🎉 All critical checks passed!")
        print("   Your code is ready for commit!")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        if not quality_passed:
            print("   💡 Run 'black .' to fix formatting issues")
        if not tests_passed:
            print("   💡 Fix failing tests before committing")

    # Exit with appropriate code
    if quality_passed and tests_passed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
