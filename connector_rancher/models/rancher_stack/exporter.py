# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import m2o_to_external


class RancherStackExportMapper(Component):
    _name = 'rancher.export.mapper.stack'
    _inherit = 'rancher.export.mapper'
    _apply_on = 'rancher.stack'

    direct = [('name', 'name'),
              ('description', 'description'),
              ('state', 'state'),
              ('answers', 'environment'),
              ('docker_compose', 'dockerCompose'),
              ('rancher_compose', 'rancherCompose'),
              ('start_on_create', 'startOnCreate'),
              (m2o_to_external('environment_id', 'rancher.environment'),
               'accountId'),
              (m2o_to_external('application_version_id',
                               'rancher.application.version'),
               'externalId'),
              ]


class RancherStackExporter(Component):
    """export one Rancher record."""
    _name = 'rancher.record.exporter.stack'
    _inherit = 'rancher.exporter'
    _apply_on = 'rancher.stack'

    def _after_export(self):
        assert self.export_result
        self.env['rancher.stack'].import_direct(
            self.backend_record, self.export_result,
        )
