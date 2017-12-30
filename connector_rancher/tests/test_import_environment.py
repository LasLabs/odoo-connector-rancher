# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import RancherSyncTestCase, recorder


class TestImportEnvironment(RancherSyncTestCase):

    UID = '1a5'

    def setUp(self):
        super(TestImportEnvironment, self).setUp()
        self.model = self.env['rancher.environment']

    @recorder.use_cassette()
    def test_import_environment(self):
        """It should import and bind the environment."""
        self._import_record()

    @recorder.use_cassette()
    def test_import_environment_links_backend(self):
        """It should add the backend reference."""
        record = self._import_record()
        self.assertEqual(record.connector, self.backend)
