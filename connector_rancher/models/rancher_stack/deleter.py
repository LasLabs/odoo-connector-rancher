# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class RancherStackDeleter(Component):
    """delete one Rancher record."""
    _name = 'rancher.record.deleter.stack'
    _inherit = 'rancher.exporter.deleter'
    _apply_on = 'rancher.stack'

    def _after_delete(self):
        assert self.delete_result
        self.env['rancher.stack'].import_direct(
            self.backend_record, self.delete_result,
        )
