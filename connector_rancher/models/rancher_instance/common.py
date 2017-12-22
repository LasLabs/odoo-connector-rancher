# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class InfrastructureInstance(models.Model):

    _inherit = 'infrastructure.instance'

    rancher_bind_ids = fields.One2many(
        string='Rancher Bindings',
        comodel_name='rancher.instance',
        inverse_name='odoo_id',
    )


class RancherInstance(models.Model):

    _name = 'rancher.instance'
    _inherit = 'rancher.binding'
    _inherits = {'infrastructure.instance': 'odoo_id'}
    _description = 'Rancher Instances'

    _rec_name = 'name'

    odoo_id = fields.Many2one(
        string='Instance',
        comodel_name='infrastructure.instance',
        required=True,
        ondelete='cascade',
    )


class RancherInstanceAdapter(Component):
    """Utilize the API in context."""
    _name = 'rancher.instance.adapter'
    _inherit = 'rancher.adapter'
    _apply_on = 'rancher.instance'
    _rancher_endpoint = 'container'
