# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import (external_to_m2o,
                                                     mapping,
                                                     only_create,
                                                     )


class RancherApplicationVersionImportMapper(Component):
    _name = 'rancher.import.mapper.application.version'
    _inherit = 'rancher.import.mapper'
    _apply_on = 'rancher.application.version'

    direct = [('version', 'name'),
              (external_to_m2o('templateId', 'rancher.application'),
               'application_id'),
              ]

    @mapping
    @only_create
    def file_ids(self, record):
        files = []
        for name, data in (record['files'] or {}).items():
            file_values = {
                'datas': base64.b64encode(data.encode('utf-8')),
                'datas_fname': name,
                'name': name,
                'type': 'binary',
                'mimetype': 'text/plain',
            }
            files.append((0, 0, file_values))
        return {'file_ids': files}

    @mapping
    def option_ids(self, record):
        options = [(5, 0, 0)]
        for question in record['questions'] or []:
            option_values = {
                'name': question['variable'],
                'description': question['description'],
                'display_name': question['label'],
                'is_required': question['required'],
                'value_default': question['default'],
            }
            options.append((0, 0, option_values))
        return {'option_ids': options}

    @mapping
    def external_id(self, record):
        return {
            'external_id': 'catalog://%s' % record['id'],
        }


class RancherApplicationVersionImporter(Component):
    """Import one Rancher record."""
    _name = 'rancher.record.importer.application.version'
    _inherit = 'rancher.importer'
    _apply_on = 'rancher.application.version'


class RancherApplicationVersionBatchImporter(Component):
    """Import a batch of Rancher records."""
    _name = 'rancher.batch.importer.application.version'
    _inherit = 'rancher.direct.batch.importer'
    _apply_on = 'rancher.application.version'
