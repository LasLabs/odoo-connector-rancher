# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class InfrastructureVolume(models.Model):

    _inherit = 'infrastructure.volume'

    rancher_bind_ids = fields.One2many(
        string='Rancher Bindings',
        comodel_name='rancher.volume',
        inverse_name='odoo_id',
    )


class RancherVolume(models.Model):

    _name = 'rancher.volume'
    _inherit = 'rancher.binding'
    _inherits = {'infrastructure.volume': 'odoo_id'}
    _description = 'Rancher Volumes'

    _rec_name = 'name'

    odoo_id = fields.Many2one(
        string='Volume',
        comodel_name='infrastructure.volume',
        required=True,
        ondelete='cascade',
    )


class RancherVolumeAdapter(Component):
    """Utilize the API in context."""
    _name = 'rancher.volume.adapter'
    _inherit = 'rancher.adapter'
    _apply_on = 'rancher.volume'
    _rancher_endpoint = 'volume'
