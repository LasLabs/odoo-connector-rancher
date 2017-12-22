# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

# pylint: disable=missing-manifest-dependency
# disable warning on 'vcr' missing in manifest: this is only a dependency for
# dev/tests

"""
Helpers usable in the tests
"""

import logging
import tempfile

import mock
import odoo

from os.path import dirname, join
from contextlib import contextmanager
from uuid import uuid4

from odoo.addons.component.tests.common import SavepointComponentCase

from vcr import VCR

logging.getLogger("vcr").setLevel(logging.WARNING)

recorder = VCR(
    record_mode='once',
    cassette_library_dir=join(dirname(__file__), 'fixtures/cassettes'),
    path_transformer=VCR.ensure_suffix('.yaml'),
    filter_headers=['Authorization'],
)


class RancherTestCase(SavepointComponentCase):
    """Base class - Test the imports from a Rancher Mock."""

    def setUp(self):
        super(RancherTestCase, self).setUp()
        # disable commits when run from pytest/nosetest
        odoo.tools.config['test_enable'] = True

        self.backend_model = self.env['rancher.backend']
        self.secret_file = tempfile.NamedTemporaryFile()
        self.secret_file.write(
            '9NCZkpKKZ4oHHHeB1Rqq9Lri48xVbx8fiKbWHuZW',
        )
        self.backend = self.backend_model.create(
            {'name': 'Test Rancher',
             'version': 'v2-beta',
             'catalog_version': 'v1-catalog',
             'host': '0.0.0.0',
             'port': 8080,
             'is_ssl': False,
             'access_key': 'C69DBC9A4341E8CF9630',
             'secret_path': self.secret_file.name,
             }
        )

    def tearDown(self):
        super(RancherTestCase, self).tearDown()
        self.secret_file.close()

    @contextmanager
    def mock_with_delay(self):
        with mock.patch(
                'odoo.addons.queue_job.models.base.DelayableRecordset',
                name='DelayableRecordset', spec=True
        ) as delayable_cls:
            # prepare the mocks
            delayable = mock.MagicMock(name='DelayableBinding')
            delayable_cls.return_value = delayable
            yield delayable_cls, delayable


class RancherSyncTestCase(RancherTestCase):

    def setUp(self):
        super(RancherSyncTestCase, self).setUp()

    def _import_record(self):
        domain = [('external_id', '=', self.UID),
                  ('backend_id', '=', self.backend.id)]
        self.assertFalse(self.model.search(domain))
        self.model.import_record(self.backend, self.UID)
        record = self.model.search(domain)
        self.assertTrue(record)
        return record

    @contextmanager
    def _export_application(self):
        self.application = self._import_record()
        self.environment = self.env['rancher.environment'].import_record(
            self.backend, '1a5',
        )
        self.wizard = self.env['infrastructure.application.deploy'].create({
            'name': uuid4(),
            'description': 'This is a test stack',
            'environment_id': self.environment.odoo_id.id,
            'application_id': self.application.odoo_id.id,
            'version_id': self.application.default_version_id.id,
        })
        odoo_stack = self.backend.deploy_application(self.wizard)
        rancher_stack = odoo_stack.rancher_bind_ids
        try:
            yield rancher_stack
        finally:
            rancher_stack.export_delete_record()
