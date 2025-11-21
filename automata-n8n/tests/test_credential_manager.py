"""
Tests for Credential Manager

Tests credential management functionality including:
- Credential template creation
- Credential validation
- Credential tracking
- Manifest export

Author: Project Automata - Agent 5 (High Priority Features)
Version: 2.1.0
Date: 2025-11-20
Issue: #9 - Credential Management
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.credential_manager import (
    CredentialTemplate,
    CredentialManager,
    CredentialLibrary,
    create_credential,
    get_common_credential
)


class TestCredentialTemplate(unittest.TestCase):
    """Test CredentialTemplate class"""

    def test_create_credential_template(self):
        """Test creating a basic credential template"""
        cred = CredentialTemplate(
            name="Test Credential",
            type="httpBasicAuth",
            description="Test description"
        )

        self.assertEqual(cred.name, "Test Credential")
        self.assertEqual(cred.type, "httpBasicAuth")
        self.assertEqual(cred.description, "Test description")
        self.assertEqual(cred.environment, "production")

    def test_to_node_reference(self):
        """Test converting credential to node reference"""
        cred = CredentialTemplate(
            name="Test Credential",
            type="httpBasicAuth"
        )

        ref = cred.to_node_reference()
        self.assertIn("name", ref)
        self.assertEqual(ref["name"], "Test Credential")

    def test_to_node_reference_with_id(self):
        """Test node reference with credential ID"""
        cred = CredentialTemplate(
            name="Test Credential",
            type="httpBasicAuth",
            credential_id="test-uuid-123"
        )

        ref = cred.to_node_reference()
        self.assertIn("id", ref)
        self.assertIn("name", ref)
        self.assertEqual(ref["id"], "test-uuid-123")

    def test_validate_valid_credential(self):
        """Test validation of valid credential"""
        cred = CredentialTemplate(
            name="Test",
            type="postgresApi"
        )

        errors = cred.validate()
        self.assertEqual(len(errors), 0)

    def test_validate_missing_name(self):
        """Test validation fails for missing name"""
        cred = CredentialTemplate(
            name="",
            type="postgresApi"
        )

        errors = cred.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("name" in err.lower() for err in errors))

    def test_validate_missing_type(self):
        """Test validation fails for missing type"""
        cred = CredentialTemplate(
            name="Test",
            type=""
        )

        errors = cred.validate()
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("type" in err.lower() for err in errors))

    def test_to_dict(self):
        """Test converting credential to dictionary"""
        cred = CredentialTemplate(
            name="Test",
            type="postgresApi",
            description="Test DB"
        )

        cred_dict = cred.to_dict()
        self.assertIsInstance(cred_dict, dict)
        self.assertEqual(cred_dict["name"], "Test")
        self.assertEqual(cred_dict["type"], "postgresApi")


class TestCredentialManager(unittest.TestCase):
    """Test CredentialManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = CredentialManager()

    def test_add_credential(self):
        """Test adding a credential"""
        cred = self.manager.add_credential(
            name="Test DB",
            credential_type="postgresApi",
            description="Test database"
        )

        self.assertIsInstance(cred, CredentialTemplate)
        self.assertEqual(cred.name, "Test DB")
        self.assertEqual(len(self.manager.credentials), 1)

    def test_get_credential(self):
        """Test retrieving a credential by name"""
        self.manager.add_credential("Test", "postgresApi")
        cred = self.manager.get_credential("Test")

        self.assertIsNotNone(cred)
        self.assertEqual(cred.name, "Test")

    def test_get_nonexistent_credential(self):
        """Test retrieving non-existent credential returns None"""
        cred = self.manager.get_credential("NonExistent")
        self.assertIsNone(cred)

    def test_list_credentials(self):
        """Test listing all credentials"""
        self.manager.add_credential("Cred1", "postgresApi")
        self.manager.add_credential("Cred2", "slackApi")

        creds = self.manager.list_credentials()
        self.assertEqual(len(creds), 2)

    def test_list_credentials_by_environment(self):
        """Test filtering credentials by environment"""
        self.manager.add_credential("Dev DB", "postgresApi", environment="development")
        self.manager.add_credential("Prod DB", "postgresApi", environment="production")

        dev_creds = self.manager.list_credentials(environment="development")
        prod_creds = self.manager.list_credentials(environment="production")

        self.assertEqual(len(dev_creds), 1)
        self.assertEqual(len(prod_creds), 1)
        self.assertEqual(dev_creds[0].name, "Dev DB")

    def test_track_node_credential(self):
        """Test tracking credential usage by nodes"""
        self.manager.add_credential("DB", "postgresApi")
        self.manager.track_node_credential("Query Node", "DB")

        self.assertIn("Query Node", self.manager.node_credential_map)
        self.assertIn("DB", self.manager.node_credential_map["Query Node"])

    def test_get_node_credentials(self):
        """Test getting credentials for a specific node"""
        self.manager.add_credential("DB", "postgresApi")
        self.manager.track_node_credential("Query Node", "DB")

        node_creds = self.manager.get_node_credentials("Query Node")
        self.assertEqual(len(node_creds), 1)
        self.assertEqual(node_creds[0].name, "DB")

    def test_get_workflow_credentials(self):
        """Test getting all credentials in workflow"""
        self.manager.add_credential("DB", "postgresApi")
        self.manager.add_credential("API", "httpHeaderAuth")

        workflow_creds = self.manager.get_workflow_credentials()
        self.assertEqual(len(workflow_creds), 2)

    def test_generate_credential_reference(self):
        """Test generating credential reference"""
        self.manager.add_credential("Test", "postgresApi")
        ref = self.manager.generate_credential_reference("Test")

        self.assertIsInstance(ref, dict)
        self.assertIn("name", ref)

    def test_generate_credential_reference_not_found(self):
        """Test generating reference for non-existent credential raises error"""
        with self.assertRaises(ValueError):
            self.manager.generate_credential_reference("NonExistent")

    def test_export_credentials_manifest(self):
        """Test exporting credentials manifest"""
        self.manager.add_credential("DB", "postgresApi")
        self.manager.add_credential("API", "httpHeaderAuth")
        self.manager.track_node_credential("Node1", "DB")

        manifest = self.manager.export_credentials_manifest()

        self.assertIn("credentials", manifest)
        self.assertIn("node_credential_map", manifest)
        self.assertIn("total_credentials", manifest)
        self.assertEqual(manifest["total_credentials"], 2)

    def test_validate_all(self):
        """Test validating all credentials"""
        self.manager.add_credential("Valid", "postgresApi")
        self.manager.add_credential("", "postgresApi")  # Invalid - no name

        errors = self.manager.validate_all()
        self.assertGreater(len(errors), 0)

    def test_save_manifest(self):
        """Test saving manifest to file"""
        self.manager.add_credential("Test", "postgresApi")

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name

        try:
            self.manager.save_manifest(filepath)
            self.assertTrue(os.path.exists(filepath))

            with open(filepath, 'r') as f:
                data = json.load(f)

            self.assertIn("credentials", data)
            self.assertIn("total_credentials", data)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestCredentialLibrary(unittest.TestCase):
    """Test CredentialLibrary class"""

    def test_http_basic_auth(self):
        """Test HTTP Basic Auth credential template"""
        cred = CredentialLibrary.http_basic_auth("Test Auth")

        self.assertEqual(cred.name, "Test Auth")
        self.assertEqual(cred.type, "httpBasicAuth")
        self.assertIn("username", cred.fields)
        self.assertIn("password", cred.fields)

    def test_http_header_auth(self):
        """Test HTTP Header Auth credential template"""
        cred = CredentialLibrary.http_header_auth("API Key", "X-API-Key")

        self.assertEqual(cred.type, "httpHeaderAuth")
        self.assertIn("name", cred.fields)
        self.assertIn("value", cred.fields)

    def test_postgres(self):
        """Test PostgreSQL credential template"""
        cred = CredentialLibrary.postgres(
            "Test DB",
            host="localhost",
            database="testdb"
        )

        self.assertEqual(cred.type, "postgresApi")
        self.assertIn("host", cred.fields)
        self.assertEqual(cred.fields["host"]["value"], "localhost")

    def test_mysql(self):
        """Test MySQL credential template"""
        cred = CredentialLibrary.mysql(
            "Test DB",
            host="db.example.com",
            database="mydb"
        )

        self.assertEqual(cred.type, "mysqlApi")
        self.assertEqual(cred.fields["port"]["value"], 3306)

    def test_mongodb(self):
        """Test MongoDB credential template"""
        cred = CredentialLibrary.mongodb(
            "Test DB",
            connection_string="mongodb://localhost:27017/test"
        )

        self.assertEqual(cred.type, "mongoDb")
        self.assertIn("connectionString", cred.fields)

    def test_slack(self):
        """Test Slack credential template"""
        cred = CredentialLibrary.slack("Team Slack")

        self.assertEqual(cred.type, "slackApi")
        self.assertIn("accessToken", cred.fields)

    def test_email_smtp(self):
        """Test SMTP email credential template"""
        cred = CredentialLibrary.email_smtp(
            "SMTP",
            host="smtp.example.com",
            port=587
        )

        self.assertEqual(cred.type, "emailSendApi")
        self.assertEqual(cred.fields["port"]["value"], 587)

    def test_aws(self):
        """Test AWS credential template"""
        cred = CredentialLibrary.aws("AWS", region="us-west-2")

        self.assertEqual(cred.type, "aws")
        self.assertEqual(cred.fields["region"]["value"], "us-west-2")

    def test_github(self):
        """Test GitHub credential template"""
        cred = CredentialLibrary.github("GitHub")

        self.assertEqual(cred.type, "githubApi")
        self.assertIn("accessToken", cred.fields)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions"""

    def test_create_credential(self):
        """Test create_credential function"""
        cred = create_credential(
            "Test",
            "postgresApi",
            description="Test DB"
        )

        self.assertIsInstance(cred, CredentialTemplate)
        self.assertEqual(cred.name, "Test")

    def test_get_common_credential_postgres(self):
        """Test getting common PostgreSQL credential"""
        cred = get_common_credential(
            'postgres',
            name="DB",
            host="localhost"
        )

        self.assertEqual(cred.type, "postgresApi")

    def test_get_common_credential_slack(self):
        """Test getting common Slack credential"""
        cred = get_common_credential('slack', name="Slack")

        self.assertEqual(cred.type, "slackApi")

    def test_get_common_credential_invalid(self):
        """Test getting invalid service raises error"""
        with self.assertRaises(ValueError):
            get_common_credential('invalid_service')


if __name__ == '__main__':
    unittest.main()
