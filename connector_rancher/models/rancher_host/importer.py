# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (external_to_m2o,
                                                     mapping,
                                                     )


class RancherHostImportMapper(Component):
    _name = 'rancher.import.mapper.host'
    _inherit = 'rancher.import.mapper'
    _apply_on = 'rancher.host'

    direct = [('hostname', 'name'),
              ('description', 'description'),
              ('state', 'state'),
              (external_to_m2o('accountId', 'rancher.environment'),
               'environment_id'),
              ]

    @mapping
    def cpu_metric_id(self, record):
        cpu_info = record['info'].cpuInfo
        mhz = self.env.ref('product_uom_technology.product_uom_mhz')
        metric = self.env['infrastructure.metric.cpu'].create({
            'name': cpu_info.modelName,
            'load_one': cpu_info.loadAvg[0],
            'load_five': cpu_info.loadAvg[1],
            'load_fifteen': cpu_info.loadAvg[2],
            'core_count': cpu_info.count,
            'frequency': cpu_info.mhz,
            'frequency_uom_id': mhz.id,
            'core_metric_ids': [
                (0, 0, {'percent_use': p})
                for p in cpu_info.cpuCoresPercentages
            ],
        })
        return {'cpu_metric_id': metric.id}

    @mapping
    def memory_metric_id(self, record):
        memory_info = record['info'].memoryInfo
        mib = self.env.ref('product_uom_technology.product_uom_mib')
        metric = self.env['infrastructure.metric.memory'].create({
            'memory_free': memory_info.memFree,
            'memory_cache': memory_info.cached,
            'memory_buffer': memory_info.buffers,
            'memory_total': memory_info.memTotal,
            'memory_available': memory_info.memAvailable,
            'memory_used': memory_info.memTotal - memory_info.memFree,
            'swap_cache': memory_info.swapCached,
            'swap_free': memory_info.swapfree,
            'swap_total': memory_info.swaptotal,
            'uom_id': mib.id,
        })
        return {'memory_metric_id': metric.id}

    @mapping
    def operating_system_id(self, record):
        regex = re.compile(r'(?P<name>.+?) (?P<version>\d+\.\d+.*)')
        matches = regex.search(record['info'].osInfo.operatingSystem)
        software = self.env['infrastructure.software.version'].get_or_create(
            name=matches.group('name').strip(),
            version=matches.group('version').strip(),
            type='os',
        )
        return {'operating_system_id': software.id}

    @mapping
    def kernel_id(self, record):
        software = self.env['infrastructure.software.version'].get_or_create(
            name='Linux',
            version=record['info'].osInfo.kernelVersion,
            type='kernel',
        )
        return {'kernel_id': software.id}

    @mapping
    def virtualization_id(self, record):
        regex = re.compile(
            r'(?P<name>.+?) (v(ersion)? ?)?(?P<version>\d+\.\d+.*)',
        )
        matches = regex.search(record['info'].osInfo.dockerVersion)
        software = self.env['infrastructure.software.version'].get_or_create(
            name=matches.group('name').strip(),
            version=matches.group('version').strip(),
            type='virtualization',
        )
        return {'virtualization_id': software.id}

    @mapping
    def label_ids(self, record):
        labels = self.env['infrastructure.option']
        for name, value in record['labels'].items():
            labels += labels.get_or_create(name, value)
        return {'label_ids': [(6, 0, labels.ids)]}


class RancherHostImporter(Component):
    """Import one Rancher record."""
    _name = 'rancher.record.importer.host'
    _inherit = 'rancher.importer'
    _apply_on = 'rancher.host'

    def _after_import(self, binding):
        """Import the file systems and mount metrics."""
        record = self.rancher_record
        disk_info = record['info'].diskInfo
        metrics = {
            name: metrics for name, metrics in disk_info.mountPoints.items()
        }
        file_systems = self.env['infrastructure.file.system']
        for name, metadata in disk_info.fileSystems.items():
            file_system = file_systems.get_or_create(
                name, binding.odoo_id, capacity=metadata['capacity'],
            )
            file_system.metric_ids = [(0, 0, metrics[name])]

        return super(RancherHostImporter, self)._after_import(binding)

    def _import_dependencies(self):
        self.env['rancher.environment'].import_record(
            self.backend_record, self.rancher_record['accountId'],
        )
        return super(RancherHostImporter, self)._import_dependencies()


class RancherHostBatchImporter(Component):
    """Import a batch of Rancher records."""
    _name = 'rancher.batch.importer.host'
    _inherit = 'rancher.direct.batch.importer'
    _apply_on = 'rancher.host'
