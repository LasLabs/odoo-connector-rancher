# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import RancherSyncTestCase, recorder


class TestImportService(RancherSyncTestCase):

    UID = '1s3'

    def setUp(self):
        super(TestImportService, self).setUp()
        self.model = self.env['rancher.service']

    @recorder.use_cassette()
    def test_import_service(self):
        """It should import and bind the service."""
        self._import_record()

    @recorder.use_cassette()
    def test_import_service_imports_environment(self):
        """It should import the environment as a dependency."""
        record = self._import_record()
        self.assertTrue(record.environment_id)

    @recorder.use_cassette()
    def test_import_service_imports_stack(self):
        """It should import the stack as a dependency."""
        record = self._import_record()
        self.assertTrue(record.stack_id)

    @recorder.use_cassette()
    def test_import_service_imports_config(self):
        """It should import the launch configuration with the service."""
        record = self._import_record()
        self.assertTrue(record.config_id.active)
