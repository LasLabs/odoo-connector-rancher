# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class InfrastructureService(models.Model):

    _inherit = 'infrastructure.service'

    rancher_bind_ids = fields.One2many(
        string='Rancher Bindings',
        comodel_name='rancher.service',
        inverse_name='odoo_id',
    )


class RancherService(models.Model):

    _name = 'rancher.service'
    _inherit = 'rancher.binding'
    _inherits = {'infrastructure.service': 'odoo_id'}
    _description = 'Rancher Services'

    _rec_name = 'name'

    odoo_id = fields.Many2one(
        string='Service',
        comodel_name='infrastructure.service',
        required=True,
        ondelete='cascade',
    )


class RancherServiceAdapter(Component):
    """Utilize the API in context."""
    _name = 'rancher.service.adapter'
    _inherit = 'rancher.adapter'
    _apply_on = 'rancher.service'
    _rancher_endpoint = 'service'
