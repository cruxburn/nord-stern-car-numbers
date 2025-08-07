#!/usr/bin/env python3
"""
Code quality checker for Nord Stern Car Numbers
Runs Black formatting check and flake8 linting
"""

import subprocess
import sys


def run_command(command, description):
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
            return False

    except Exception as e:
        print(f"   ❌ Error running {description}: {e}")
        return False


def main():
    """Main quality checker"""
    print("🎨 Nord Stern Car Numbers - Code Quality Checker")
    print("=" * 50)

    # Check Black formatting
    black_success = run_command("black --check --diff .", "Black code formatting check")

    # Run flake8 for critical issues only
    flake8_success = run_command(
        "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics",
        "Flake8 critical linting check",
    )

    # Summary
    print("\n" + "=" * 50)
    print("📋 Quality Check Summary")
    print("=" * 50)
    print(f"   Black Formatting: {'✅ PASSED' if black_success else '❌ FAILED'}")
    print(f"   Flake8 Linting:   {'✅ PASSED' if flake8_success else '❌ FAILED'}")

    if black_success and flake8_success:
        print("\n🎉 All quality checks passed!")
        print("   Your code meets quality standards!")
    else:
        print("\n⚠️  Some quality checks failed.")
        if not black_success:
            print("   💡 To fix Black formatting issues, run: black .")
        if not flake8_success:
            print(
                "   💡 To see all flake8 issues, run: flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics"
            )

    # Exit with appropriate code
    if black_success and flake8_success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
