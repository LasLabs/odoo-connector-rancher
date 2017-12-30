# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import RancherSyncTestCase, recorder


class TestImportApplication(RancherSyncTestCase):

    UID = 'library:infra*ecr'

    def setUp(self):
        super(TestImportApplication, self).setUp()
        self.model = self.env['rancher.application']

    @recorder.use_cassette()
    def test_import_application(self):
        """It should import and bind the application."""
        self._import_record()

    @recorder.use_cassette()
    def test_import_application_imports_versions(self):
        """It should import the versions."""
        record = self._import_record()
        self.assertTrue(record.version_ids)

    @recorder.use_cassette()
    def test_import_application_imports_default_version(self):
        """It should import the default version."""
        record = self._import_record()
        self.assertTrue(record.default_version_id)

    @recorder.use_cassette()
    def test_import_application_version_docker_compose(self):
        """It should import the docker-compose.yml file."""
        record = self._import_record()
        self.assertTrue(
            record.default_version_id.get_file_by_name(
                'docker-compose.yml.tpl',
            ),
        )

    @recorder.use_cassette()
    def test_import_application_version_rancher_compose(self):
        """It should import the rancher-compose.yml file."""
        record = self._import_record()
        self.assertTrue(
            record.default_version_id.get_file_by_name('rancher-compose.yml'),
        )

    @recorder.use_cassette()
    def test_import_application_imports_version_options(self):
        """It should import the application version questions."""
        record = self._import_record()
        self.assertTrue(record.default_version_id.option_ids[0].name)
