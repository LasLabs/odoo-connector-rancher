# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class InfrastructureHost(models.Model):

    _inherit = 'infrastructure.host'

    rancher_bind_ids = fields.One2many(
        string='Rancher Bindings',
        comodel_name='rancher.host',
        inverse_name='odoo_id',
    )


class RancherHost(models.Model):

    _name = 'rancher.host'
    _inherit = 'rancher.binding'
    _inherits = {'infrastructure.host': 'odoo_id'}
    _description = 'Rancher Hosts'

    _rec_name = 'name'

    odoo_id = fields.Many2one(
        string='Host',
        comodel_name='infrastructure.host',
        required=True,
        ondelete='cascade',
    )


class RancherHostAdapter(Component):
    """Utilize the API in context."""
    _name = 'rancher.host.adapter'
    _inherit = 'rancher.adapter'
    _apply_on = 'rancher.host'
    _rancher_endpoint = 'host'
