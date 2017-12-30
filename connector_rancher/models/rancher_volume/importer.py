# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import external_to_m2o, mapping


class RancherVolumeImportMapper(Component):
    _name = 'rancher.import.mapper.volume'
    _inherit = 'rancher.import.mapper'
    _apply_on = 'rancher.volume'

    direct = [('name', 'name'),
              ('externalId', 'external_name'),
              ('state', 'state'),
              ('accessMode', 'access_mode'),
              ('driver', 'driver'),
              ('isHostPath', 'is_host_path'),
              ('kind', 'type'),
              ('size_mb', 'capacity'),
              (external_to_m2o('accountId', 'rancher.environment'),
               'environment_id'),
              (external_to_m2o('hostId', 'rancher.host'),
               'host_id'),
              ]

    @mapping
    def capacity_uom_id(self, _):
        mib = self.env.ref('product_uom_technology.product_uom_gib')
        return {'capacity_uom_id': mib.id}


class RancherVolumeImporter(Component):
    """Import one Rancher record."""
    _name = 'rancher.record.importer.volume'
    _inherit = 'rancher.importer'
    _apply_on = 'rancher.volume'

    def _import_dependencies(self):
        self.env['rancher.environment'].import_record(
            self.backend_record, self.rancher_record['accountId'],
        )
        return super(RancherVolumeImporter, self)._import_dependencies()


class RancherVolumeBatchImporter(Component):
    """Import a batch of Rancher records."""
    _name = 'rancher.batch.importer.volume'
    _inherit = 'rancher.direct.batch.importer'
    _apply_on = 'rancher.volume'
