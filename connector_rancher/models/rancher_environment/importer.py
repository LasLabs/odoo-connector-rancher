# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class RancherEnvironmentImportMapper(Component):
    _name = 'rancher.import.mapper.environment'
    _inherit = 'rancher.import.mapper'
    _apply_on = 'rancher.environment'

    direct = [('name', 'name'),
              ('description', 'description'),
              ('state', 'state'),
              ('healthState', 'state_health'),
              ]

    @mapping
    def connector(self, _record):
        return {
            'connector': '%s,%s' % (
                self.backend_record._name, self.backend_record.id,
            ),
        }

    @mapping
    def company_ids(self, _record):
        return {
            'company_ids': [(6, 0, self.backend_record.company_ids.ids)],
        }


class RancherEnvironmentImporter(Component):
    """Import one Rancher record."""
    _name = 'rancher.record.importer.environment'
    _inherit = 'rancher.importer'
    _apply_on = 'rancher.environment'


class RancherEnvironmentBatchImporter(Component):
    """Import a batch of Rancher records."""
    _name = 'rancher.batch.importer.environment'
    _inherit = 'rancher.direct.batch.importer'
    _apply_on = 'rancher.environment'
