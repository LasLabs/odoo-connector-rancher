# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class InfrastructureApplicationVersion(models.Model):

    _inherit = 'infrastructure.application.version'

    rancher_bind_ids = fields.One2many(
        string='Rancher Bindings',
        comodel_name='rancher.application.version',
        inverse_name='odoo_id',
    )


class RancherApplicationVersion(models.Model):

    _name = 'rancher.application.version'
    _inherit = 'rancher.binding'
    _inherits = {'infrastructure.application.version': 'odoo_id'}
    _description = 'Rancher Application Versions'

    _rec_name = 'name'

    USE_CATALOG_API = True

    odoo_id = fields.Many2one(
        string='Application Version',
        comodel_name='infrastructure.application.version',
        required=True,
        ondelete='cascade',
    )


class RancherApplicationVersionAdapter(Component):
    """Utilize the API in context."""
    _name = 'rancher.application.version.adapter'
    _inherit = 'rancher.adapter'
    _apply_on = 'rancher.application.version'
    _rancher_endpoint = 'template'

    def _strip_catalog_id(self, _id):
        return _id.replace('catalog://', '')

    def _add_catalog_id(self, _id):
        return 'catalog://%s' % id

    def read(self, _id, *args, **kwargs):
        return super(RancherApplicationVersionAdapter, self).read(
            self._strip_catalog_id(_id), *args, **kwargs
        )

    def search(self, **query):
        results = super(RancherApplicationVersionAdapter, self).search(
            **query
        )
        return [self._add_catalog_id(i) for i in results]

    def write(self, _id, data):
        raise NotImplementedError

    def delete(self, _id):
        raise NotImplementedError

    def create(self, data):
        raise NotImplementedError
