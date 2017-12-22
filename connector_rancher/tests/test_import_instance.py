# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import RancherSyncTestCase, recorder


class TestImportInstance(RancherSyncTestCase):

    UID = '1i4'

    def setUp(self):
        super(TestImportInstance, self).setUp()
        self.model = self.env['rancher.instance']

    @recorder.use_cassette()
    def test_import_instance(self):
        """It should import and bind the instance."""
        self._import_record()

    @recorder.use_cassette()
    def test_import_instance_imports_service(self):
        """It should import the service as a dependency."""
        record = self._import_record()
        self.assertTrue(record.service_id)

    @recorder.use_cassette()
    def test_import_instance_imports_stack(self):
        """It should import the stack implicitly with the service."""
        record = self._import_record()
        self.assertTrue(record.stack_id)

    @recorder.use_cassette()
    def test_import_instance_imports_host(self):
        """It should import the host as a dependency."""
        record = self._import_record()
        self.assertTrue(record.stack_id)

    @recorder.use_cassette()
    def test_import_instance_imports_environment(self):
        """It should import the environment implicitly with the host."""
        record = self._import_record()
        self.assertTrue(record.host_id)

    @recorder.use_cassette()
    def test_import_instance_imports_launch_config(self):
        """It should import the launch config with the instance."""
        record = self._import_record()
        self.assertTrue(record.config_id.active)
