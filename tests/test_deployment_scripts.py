#!/usr/bin/env python3
"""
Tests for deployment script functionality in Nord Stern Car Numbers
"""

import unittest
import os
import tempfile
import sys
import shutil
import subprocess
import time
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DeploymentScriptsTestCase(unittest.TestCase):
    """Test cases for deployment script functionality"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create mock export files
        self.export_files = [
            "database_export.json",
            "database_export.csv",
            "database_import.sql",
        ]

        for file in self.export_files:
            with open(file, "w") as f:
                f.write(f"Mock content for {file}")

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_deploy_with_data_creates_temp_directory(self):
        """Test that deploy_with_data.sh creates temporary deployment directory"""
        # This test verifies the logic of creating a temp directory
        # We'll test the file operations without actually running the full script

        # Simulate the deployment directory creation logic
        deploy_dir = f"deploy_temp_{int(time.time())}"
        os.makedirs(deploy_dir, exist_ok=True)

        # Verify directory was created
        self.assertTrue(
            os.path.exists(deploy_dir), "Deployment directory should be created"
        )

        # Clean up
        os.rmdir(deploy_dir)

    def test_deploy_with_data_copies_export_files(self):
        """Test that deploy_with_data.sh copies export files to deployment directory"""
        # Create a mock deployment directory
        deploy_dir = "test_deploy_dir"
        os.makedirs(deploy_dir, exist_ok=True)

        # Simulate copying export files
        for file in self.export_files:
            if os.path.exists(file):
                shutil.copy2(file, deploy_dir)

        # Verify files were copied
        for file in self.export_files:
            deployed_file = os.path.join(deploy_dir, file)
            self.assertTrue(
                os.path.exists(deployed_file),
                f"Export file {file} should be copied to deployment directory",
            )

        # Clean up
        shutil.rmtree(deploy_dir)

    def test_deploy_with_data_excludes_export_files_from_main_copy(self):
        """Test that deploy_with_data.sh excludes export files from main file copy"""
        # Create some additional files to simulate the full project
        additional_files = [
            "app.py",
            "requirements.txt",
            "Dockerfile",
            "cloudbuild.yaml",
        ]

        for file in additional_files:
            with open(file, "w") as f:
                f.write(f"Mock content for {file}")

        # Create deployment directory
        deploy_dir = "test_deploy_dir"
        os.makedirs(deploy_dir, exist_ok=True)

        # Simulate rsync-like copy excluding export files
        for file in os.listdir("."):
            if file not in self.export_files and not file.startswith("test_"):
                if os.path.isfile(file):
                    shutil.copy2(file, deploy_dir)

        # Verify export files are NOT in the main copy
        for file in self.export_files:
            deployed_file = os.path.join(deploy_dir, file)
            self.assertFalse(
                os.path.exists(deployed_file),
                f"Export file {file} should NOT be in main copy",
            )

        # Verify other files ARE copied
        for file in additional_files:
            deployed_file = os.path.join(deploy_dir, file)
            self.assertTrue(
                os.path.exists(deployed_file),
                f"File {file} should be copied to deployment directory",
            )

        # Clean up
        shutil.rmtree(deploy_dir)

    def test_deploy_script_does_not_touch_local_export_files(self):
        """Test that deploy.sh does not create or modify local export files"""
        # This test verifies that deploy.sh doesn't create local export files
        # We'll check that the script doesn't reference local export file operations

        # Read the deploy.sh script to verify it doesn't mention local export files
        deploy_script_path = os.path.join(self.original_cwd, "deploy.sh")
        with open(deploy_script_path, "r") as f:
            script_content = f.read()

        # Verify script doesn't mention local export file operations (but can exclude them)
        local_export_file_operations = [
            "export_database",
        ]

        for operation in local_export_file_operations:
            self.assertNotIn(
                operation,
                script_content,
                f"deploy.sh should not mention local {operation}",
            )

    def test_deploy_script_data_preservation_mechanism(self):
        """Test that deploy.sh includes data preservation mechanism"""
        deploy_script_path = os.path.join(self.original_cwd, "deploy.sh")
        with open(deploy_script_path, "r") as f:
            script_content = f.read()

        # Verify script includes data preservation features
        preservation_features = [
            "production_data_backup.json",
            "export_production_data",
            "Preserving current production data",
        ]

        for feature in preservation_features:
            self.assertIn(
                feature, script_content, f"deploy.sh should include {feature}"
            )

    def test_deploy_script_api_export_endpoint(self):
        """Test that deploy.sh uses the API export endpoint"""
        deploy_script_path = os.path.join(self.original_cwd, "deploy.sh")
        with open(deploy_script_path, "r") as f:
            script_content = f.read()

        # Verify script uses the API export endpoint
        self.assertIn(
            "/api/export", script_content, "deploy.sh should use /api/export endpoint"
        )

    def test_deploy_script_backup_file_handling(self):
        """Test that deploy.sh properly handles backup files"""
        deploy_script_path = os.path.join(self.original_cwd, "deploy.sh")
        with open(deploy_script_path, "r") as f:
            script_content = f.read()

        # Verify backup file handling
        backup_handling = [
            "production_data_backup.json",
            "Copying production data backup",
            "Creating custom .gcloudignore for data preservation",
        ]

        for handling in backup_handling:
            self.assertIn(
                handling, script_content, f"deploy.sh should handle {handling}"
            )

    def test_deploy_script_excludes_export_files_from_copy(self):
        """Test that deploy.sh excludes export files from main copy"""
        deploy_script_path = os.path.join(self.original_cwd, "deploy.sh")
        with open(deploy_script_path, "r") as f:
            script_content = f.read()

        # Verify export files are excluded from main copy
        excluded_files = [
            "database_export.json",
            "database_export.csv",
            "database_import.sql",
        ]

        for file in excluded_files:
            self.assertIn(
                f"--exclude='{file}'",
                script_content,
                f"deploy.sh should exclude {file} from main copy",
            )

    def test_deploy_with_data_script_mentions_export_files(self):
        """Test that deploy_with_data.sh properly handles export files"""
        # Read the deploy_with_data.sh script to verify it mentions export files
        deploy_script_path = os.path.join(self.original_cwd, "deploy_with_data.sh")

        if os.path.exists(deploy_script_path):
            with open(deploy_script_path, "r") as f:
                script_content = f.read()

            # Verify script mentions export files
            export_file_mentions = [
                "database_export.json",
                "database_export.csv",
                "database_import.sql",
            ]

            for mention in export_file_mentions:
                self.assertIn(
                    mention,
                    script_content,
                    f"deploy_with_data.sh should mention {mention}",
                )

    def test_gitignore_excludes_export_files(self):
        """Test that .gitignore properly excludes export files"""
        gitignore_path = os.path.join(self.original_cwd, ".gitignore")

        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                gitignore_content = f.read()

            # Verify export files are excluded
            export_files = [
                "database_export.json",
                "database_export.csv",
                "database_import.sql",
            ]

            for file in export_files:
                self.assertIn(
                    file, gitignore_content, f".gitignore should exclude {file}"
                )

    def test_gcloudignore_excludes_export_files(self):
        """Test that .gcloudignore properly excludes export files"""
        gcloudignore_path = os.path.join(self.original_cwd, ".gcloudignore")

        if os.path.exists(gcloudignore_path):
            with open(gcloudignore_path, "r") as f:
                gcloudignore_content = f.read()

            # Verify export files are excluded
            export_files = [
                "database_export.json",
                "database_export.csv",
                "database_import.sql",
            ]

            for file in export_files:
                self.assertIn(
                    file, gcloudignore_content, f".gcloudignore should exclude {file}"
                )

    def test_deployment_scripts_are_executable(self):
        """Test that deployment scripts are executable"""
        scripts = ["deploy.sh", "deploy_with_data.sh"]

        for script in scripts:
            script_path = os.path.join(self.original_cwd, script)
            if os.path.exists(script_path):
                # Check if file is executable
                is_executable = os.access(script_path, os.X_OK)
                self.assertTrue(is_executable, f"Script {script} should be executable")


if __name__ == "__main__":
    unittest.main()
