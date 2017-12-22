# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class RancherApplicationImportMapper(Component):
    _name = 'rancher.import.mapper.application'
    _inherit = 'rancher.import.mapper'
    _apply_on = 'rancher.application'

    direct = [('name', 'name'),
              ('description', 'description'),
              ('license', 'license'),
              ('maintainer', 'maintainer'),
              ('isSystem', 'is_system'),
              ]

    @mapping
    def label_ids(self, record):
        labels = self.env['infrastructure.option']
        for name, value in (record['labels'] or {}).items():
            labels += labels.get_or_create(name, value)
        return {'label_ids': [(6, 0, labels.ids)]}

    @mapping
    def category_ids(self, record):
        labels = self.env['infrastructure.option']
        for name in (record['categories'] or []):
            labels += labels.get_or_create('application.category', name)
        return {'category_ids': [(6, 0, labels.ids)]}


class RancherApplicationImporter(Component):
    """Import one Rancher record."""
    _name = 'rancher.record.importer.application'
    _inherit = 'rancher.importer'
    _apply_on = 'rancher.application'

    def _after_import(self, binding):

        # Import the versions
        for version_link in self.rancher_record['versionLinks'].values():
            version_id = version_link.split('/')[-1]
            self.env['rancher.application.version'].import_record(
                self.backend_record, version_id,
            )

        # Assign the default
        binder = self.binder_for('rancher.application.version')
        default_version = binder.to_internal(
            self.rancher_record['defaultTemplateVersionId'], unwrap=True,
        )
        if default_version and binding.default_version_id != default_version:
            binding.default_version_id = default_version

        return super(RancherApplicationImporter, self)._after_import(binding)


class RancherApplicationBatchImporter(Component):
    """Import a batch of Rancher records."""
    _name = 'rancher.batch.importer.application'
    _inherit = 'rancher.direct.batch.importer'
    _apply_on = 'rancher.application'
