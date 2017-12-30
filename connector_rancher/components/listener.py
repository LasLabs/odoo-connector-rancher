# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class RancherListener(Component):
    """Generic event listener for Rancher."""
    _name = 'rancher.listener'
    _inherit = 'base.event.listener'

    def no_connector_export(self, record):
        return self.env.context.get('connector_no_export')

    def export_record(self, record, fields=None, with_delay=True):
        record = with_delay and record.with_delay() or record
        record.export_record(fields=fields)

    def delete_record(self, record, with_delay=True):
        record = with_delay and record.with_delay() or record
        record.export_delete_record()


class RancherListenerBindingCreateUpdate(Component):
    """Generic event listener for Rancher bindings for create/update.
    """
    _name = 'rancher.listener.binding.create.update'
    _inherit = 'rancher.listener'
    _apply_on = []

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        self.export_record(record, fields, with_delay=False)

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        self.export_record(record, fields, with_delay=False)


class RancherListenerBindingAll(Component):
    """Generic event listener for Rancher bindings, all CRUD."""
    _name = 'rancher.listener.binding.all'
    _inherit = 'rancher.listener.binding.create.update'
    _apply_on = [
        'rancher.stack',
    ]

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_unlink(self, record):
        self.delete_record(record, with_delay=False)


class RancherListenerOdooUnlink(Component):
    """Generic event listener for Odoo models unlink"""

    _name = 'rancher.listener.odoo.unlink'
    _inherit = 'rancher.listener'
    _apply_on = []

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_unlink(self, record):
        if not record.rancher_bind_ids:
            return
        self.delete_record(record.rancher_bind_ids, with_delay=False)


class RancherListenerOdooAll(Component):
    """Generic event listener for Odoo models all CRUD."""
    _name = 'rancher.listener.odoo.all'
    _inherit = 'rancher.listener.odoo.unlink'
    _apply_on = [
        'infrastructure.stack',
    ]

    def new_binding(self, record):
        exporter = self.env['rancher.backend'].default_exporter
        if exporter:
            return self.env[self._binding_model].create({
                'odoo_id': record.id,
                'backend_id': exporter.id,
            })

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        self.export_record(record.rancher_bind_ids, fields)

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        if not record.rancher_bind_ids:
            return
        self.export_record(record.rancher_bind_ids, fields)
