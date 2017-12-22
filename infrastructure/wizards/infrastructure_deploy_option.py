# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class InfrastructureDeployOption(models.TransientModel):

    _name = 'infrastructure.deploy.option'
    _inherit = 'infrastructure.application.option'
    _description = 'Infrastructure Deploy Options'

    deployer_id = fields.Many2one(
        string='Deployer',
        comodel_name='infrastructure.application.deploy',
        ondelete='cascade',
        required=True,
    )
