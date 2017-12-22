# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class InfrastructureEnvironment(models.Model):

    _inherit = 'infrastructure.environment'

    rancher_bind_ids = fields.One2many(
        string='Rancher Bindings',
        comodel_name='rancher.environment',
        inverse_name='odoo_id',
    )
    connector = fields.Reference(
        selection_add=[('rancher.backend', 'Rancher')],
    )


class RancherEnvironment(models.Model):

    _name = 'rancher.environment'
    _inherit = 'rancher.binding'
    _inherits = {'infrastructure.environment': 'odoo_id'}
    _description = 'Rancher Environments'

    _rec_name = 'name'

    odoo_id = fields.Many2one(
        string='Environment',
        comodel_name='infrastructure.environment',
        required=True,
        ondelete='cascade',
    )


class RancherEnvironmentAdapter(Component):
    """Utilize the API in context."""
    _name = 'rancher.environment.adapter'
    _inherit = 'rancher.adapter'
    _apply_on = 'rancher.environment'
    _rancher_endpoint = 'project'
