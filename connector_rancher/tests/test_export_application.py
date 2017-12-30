# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import RancherSyncTestCase, recorder


class TestExportApplication(RancherSyncTestCase):

    UID = 'library:infra*ecr'

    def setUp(self):
        super(TestExportApplication, self).setUp()
        self.model = self.env['rancher.application']

    @recorder.use_cassette()
    def test_export_application_creates_stack(self):
        with self._export_application() as stack:
            self.assertTrue(stack)

    @recorder.use_cassette()
    def test_export_application_imports_stack_status(self):
        with self._export_application() as stack:
            self.assertEqual(stack.state, 'activating')
