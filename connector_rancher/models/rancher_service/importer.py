# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import external_to_m2o

from ...components.mapper import config_serialized


class RancherServiceImportMapper(Component):
    _name = 'rancher.import.mapper.service'
    _inherit = 'rancher.import.mapper'
    _apply_on = 'rancher.service'

    direct = [('name', 'name'),
              ('description', 'description'),
              ('state', 'state'),
              ('scale', 'scale_max'),
              ('healthState', 'state_health'),
              ('scale', 'scale_current'),
              (external_to_m2o('accountId', 'rancher.environment'),
               'environment_id'),
              (external_to_m2o('stackId', 'rancher.stack'),
               'stack_id'),
              ]

    config_serialized = config_serialized


class RancherServiceImporter(Component):
    """Import one Rancher record."""
    _name = 'rancher.record.importer.service'
    _inherit = 'rancher.importer'
    _apply_on = 'rancher.service'

    def _import_dependencies(self):
        if self.rancher_record.get('stackId'):
            self.env['rancher.stack'].import_record(
                self.backend_record, self.rancher_record['stackId'],
            )
        self.env['rancher.environment'].import_record(
            self.backend_record, self.rancher_record['accountId'],
        )

        return super(RancherServiceImporter, self)._import_dependencies()


class RancherServiceBatchImporter(Component):
    """Import a batch of Rancher records."""
    _name = 'rancher.batch.importer.service'
    _inherit = 'rancher.direct.batch.importer'
    _apply_on = 'rancher.service'
