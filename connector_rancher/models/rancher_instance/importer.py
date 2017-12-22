# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import external_to_m2o, mapping


class RancherInstanceImportMapper(Component):
    _name = 'rancher.import.mapper.instance'
    _inherit = 'rancher.import.mapper'
    _apply_on = 'rancher.instance'

    direct = [('name', 'name'),
              ('description', 'description'),
              ('state', 'state'),
              ('healthState', 'state_health'),
              (external_to_m2o('accountId', 'rancher.environment'),
               'environment_id'),
              (external_to_m2o('hostId', 'rancher.host'),
               'host_id'),
              ]

    @mapping
    def service_and_stack_id(self, record):
        if not record.get('serviceIds'):
            return
        service = self.env['rancher.service'].search([
            ('backend_id', '=', self.backend_record.id),
            ('external_id', '=', record['serviceIds'][0])
        ])
        if service:
            return {'service_id': service.odoo_id.id,
                    'stack_id': service.stack_id.id,
                    }

    @mapping
    def mount_ids(self, record):
        binder = self.binder_for('rancher.volume')
        mounts = [(5, 0, 0)]
        for mount in record['mounts'] or []:
            volume = binder.to_internal(mount.volumeId, unwrap=True)
            values = {
                'volume_id': volume.id,
                'path': mount.path,
                'is_read_only': mount.permission == 'ro',
            }
            mounts.append((0, 0, values))
        return {'mount_ids': mounts}


class RancherInstanceImporter(Component):
    """Import one Rancher record."""
    _name = 'rancher.record.importer.instance'
    _inherit = 'rancher.importer'
    _apply_on = 'rancher.instance'

    def _import_dependencies(self):
        if self.rancher_record.get('serviceIds'):
            self.env['rancher.service'].import_record(
                self.backend_record, self.rancher_record['serviceIds'][0],
            )
        self.env['rancher.host'].import_record(
            self.backend_record, self.rancher_record['hostId'],
        )
        for mount in self.rancher_record['mounts'] or []:
            self.env['rancher.volume'].import_record(
                self.backend_record, mount.volumeId,
            )

        return super(RancherInstanceImporter, self)._import_dependencies()


class RancherInstanceBatchImporter(Component):
    """Import a batch of Rancher records."""
    _name = 'rancher.batch.importer.instance'
    _inherit = 'rancher.direct.batch.importer'
    _apply_on = 'rancher.instance'
