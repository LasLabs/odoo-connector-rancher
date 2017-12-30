# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import RancherSyncTestCase, recorder


class TestImportStack(RancherSyncTestCase):

    UID = '1st3'

    def setUp(self):
        super(TestImportStack, self).setUp()
        self.model = self.env['rancher.stack']

    @recorder.use_cassette()
    def test_import_stack(self):
        """It should import and bind the stack."""
        self._import_record()

    @recorder.use_cassette()
    def test_import_stack_imports_environment(self):
        """It should import the environment as a dependency."""
        record = self._import_record()
        self.assertTrue(record.environment_id)
