# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from .common import RancherSyncTestCase, recorder


class TestImportHost(RancherSyncTestCase):

    UID = '1h1'

    def setUp(self):
        super(TestImportHost, self).setUp()
        self.model = self.env['rancher.host']

    @recorder.use_cassette()
    def test_import_host(self):
        """It should import and bind the host."""
        self._import_record()

    @recorder.use_cassette()
    def test_import_host_memory_metrics(self):
        """It should import memory metrics for the host."""
        record = self._import_record()
        self.assertTrue(record.memory_metric_ids[0].memory_free)

    @recorder.use_cassette()
    def test_import_host_cpu_metrics(self):
        """It should import cpu metrics for the host."""
        record = self._import_record()
        self.assertTrue(record.cpu_metric_ids[0].core_count)

    @recorder.use_cassette()
    def test_import_host_cpu_core_metrics(self):
        """It should import cpu core metrics for the host."""
        record = self._import_record()
        self.assertTrue(
            record.cpu_metric_ids[0].core_metric_ids[0].percent_use,
        )

    @recorder.use_cassette()
    def test_import_host_labels(self):
        """It should import the host labels."""
        record = self._import_record()
        self.assertIn('test_label', record.label_ids.mapped('name'))
        self.assertIn('label_value', record.label_ids.mapped('value'))

    @recorder.use_cassette()
    def test_import_host_operating_system(self):
        """It should save the Operating System correctly."""
        record = self._import_record()
        self.assertEqual(record.operating_system_id.name, 'Ubuntu')
        self.assertEqual(record.operating_system_id.version, '16.04.3 LTS')

    @recorder.use_cassette()
    def test_import_host_docker_version(self):
        """It should save the Docker version correctly."""
        record = self._import_record()
        self.assertEqual(record.virtualization_id.name, 'Docker')
        self.assertEqual(record.virtualization_id.version,
                         '17.09.1-ce, build 19e2cf6')

    @recorder.use_cassette()
    def test_import_host_kernel(self):
        """It should save the kernel version correctly."""
        record = self._import_record()
        self.assertEqual(record.kernel_id.name, 'Linux')
        self.assertEqual(record.kernel_id.version, '4.4.0')

    @recorder.use_cassette()
    def test_import_host_imports_file_systems(self):
        """It should import the file systems."""
        record = self._import_record()
        self.assertTrue(record.file_system_ids)

    @recorder.use_cassette()
    def test_import_host_imports_file_system_metrics(self):
        """It should import the file system metrics."""
        record = self._import_record()
        self.assertTrue(record.file_system_ids[:1].metric_id)
