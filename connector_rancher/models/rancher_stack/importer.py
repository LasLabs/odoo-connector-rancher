# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import external_to_m2o


class RancherStackImportMapper(Component):
    _name = 'rancher.import.mapper.stack'
    _inherit = 'rancher.import.mapper'
    _apply_on = 'rancher.stack'

    direct = [('name', 'name'),
              ('description', 'description'),
              ('state', 'state'),
              ('healthState', 'state_health'),
              (external_to_m2o('accountId', 'rancher.environment'),
               'environment_id'),
              ]


class RancherStackImporter(Component):
    """Import one Rancher record."""
    _name = 'rancher.record.importer.stack'
    _inherit = 'rancher.importer'
    _apply_on = 'rancher.stack'

    def _import_dependencies(self):
        self.env['rancher.environment'].import_record(
            self.backend_record, self.rancher_record['accountId'],
        )
        return super(RancherStackImporter, self)._import_dependencies()


class RancherStackBatchImporter(Component):
    """Import a batch of Rancher records."""
    _name = 'rancher.batch.importer.stack'
    _inherit = 'rancher.direct.batch.importer'
    _apply_on = 'rancher.stack'
