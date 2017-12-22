# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class InfrastructureApplication(models.Model):

    _inherit = 'infrastructure.application'

    rancher_bind_ids = fields.One2many(
        string='Rancher Bindings',
        comodel_name='rancher.application',
        inverse_name='odoo_id',
    )


class RancherApplication(models.Model):

    _name = 'rancher.application'
    _inherit = 'rancher.binding'
    _inherits = {'infrastructure.application': 'odoo_id'}
    _description = 'Rancher Applications'

    _rec_name = 'name'

    USE_CATALOG_API = True

    odoo_id = fields.Many2one(
        string='Application',
        comodel_name='infrastructure.application',
        required=True,
        ondelete='cascade',
    )


class RancherApplicationAdapter(Component):
    """Utilize the API in context."""
    _name = 'rancher.application.adapter'
    _inherit = 'rancher.adapter'
    _apply_on = 'rancher.application'
    _rancher_endpoint = 'template'
