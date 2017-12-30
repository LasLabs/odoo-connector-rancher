# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import RancherSyncTestCase, recorder


class TestCommonBackend(RancherSyncTestCase):

    UID = '1s3'  # This is a container

    def setUp(self):
        super(TestCommonBackend, self).setUp()
        self.model = self.env['rancher.service']

    def _test_cron(self, model_name):
        domain = [('backend_id', '=', self.backend.id)]
        model = self.env[model_name]
        self.assertFalse(model.search(domain))
        self.backend._cron_get_remote_records(model._name)
        self.assertTrue(model.search(domain))

    @recorder.use_cassette()
    def test_backend_cron_instances(self):
        """It should import the instances."""
        self._test_cron('rancher.instance')

    @recorder.use_cassette()
    def test_backend_cron_applications(self):
        """It should import the catalog templates."""
        self._test_cron('rancher.application')
