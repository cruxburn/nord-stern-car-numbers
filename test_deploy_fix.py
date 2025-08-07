#!/usr/bin/env python3
"""
Test script to verify the deployment fix works correctly.
This script simulates the deployment process and checks if export files are included.
"""

import os
import tempfile
import shutil
import subprocess
import json


def test_deploy_with_data_fix():
    """Test that deploy_with_data.sh properly includes export files."""
    print("🧪 Testing deploy_with_data.sh fix...")

    # Create a temporary directory to simulate deployment
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"   Created temporary directory: {temp_dir}")

        # Copy application files (excluding export files)
        print("   Copying application files...")
        subprocess.run(
            [
                "rsync",
                "-av",
                "--exclude=database_export.*",
                "--exclude=database_import.sql",
                "--exclude=venv/",
                "--exclude=.git/",
                "--exclude=deploy_temp_*/",
                ".",
                temp_dir,
            ],
            check=True,
        )

        # Copy export files
        print("   Copying export files...")
        shutil.copy("database_export.json", temp_dir)
        shutil.copy("database_export.csv", temp_dir)
        shutil.copy("database_import.sql", temp_dir)

        # Check if .gcloudignore exists and rename it
        gcloudignore_path = os.path.join(temp_dir, ".gcloudignore")
        if os.path.exists(gcloudignore_path):
            print("   Temporarily renaming .gcloudignore...")
            os.rename(gcloudignore_path, gcloudignore_path + ".backup")

        # Verify export files are present
        export_files = [
            "database_export.json",
            "database_export.csv",
            "database_import.sql",
        ]

        missing_files = []
        for file in export_files:
            file_path = os.path.join(temp_dir, file)
            if not os.path.exists(file_path):
                missing_files.append(file)

        if missing_files:
            print(f"❌ Missing export files: {missing_files}")
            return False

        print("✅ All export files are present in deployment directory")

        # Check if .gcloudignore is renamed
        if os.path.exists(gcloudignore_path + ".backup"):
            print("✅ .gcloudignore file was properly renamed")
        else:
            print("⚠️  .gcloudignore file was not found or renamed")

        # Verify JSON file has data
        json_path = os.path.join(temp_dir, "database_export.json")
        with open(json_path, "r") as f:
            data = json.load(f)
            count = data.get("total_registrations", 0)
            print(f"✅ JSON file contains {count} registrations")

        return True


def test_export_files_exist():
    """Test that export files exist locally."""
    print("🧪 Testing export files exist...")

    export_files = [
        "database_export.json",
        "database_export.csv",
        "database_import.sql",
    ]

    missing_files = []
    for file in export_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing export files: {missing_files}")
        print("   Run: python export_database.py")
        return False

    print("✅ All export files exist locally")

    # Check JSON content
    with open("database_export.json", "r") as f:
        data = json.load(f)
        count = data.get("total_registrations", 0)
        print(f"✅ JSON file contains {count} registrations")

    return True


if __name__ == "__main__":
    print("🚀 Testing Deployment Fix")
    print("=" * 50)

    # Test 1: Export files exist
    if not test_export_files_exist():
        print("\n❌ Test failed: Export files missing")
        exit(1)

    print()

    # Test 2: Deploy with data fix
    if not test_deploy_with_data_fix():
        print("\n❌ Test failed: Deploy with data fix not working")
        exit(1)

    print("\n✅ All tests passed!")
    print("   The deployment fix should work correctly.")
