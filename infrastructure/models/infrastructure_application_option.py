# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class InfrastructureApplicationOption(models.Model):

    _name = 'infrastructure.application.option'
    _description = 'Infrastructure Application Options'

    name = fields.Char(
        required=True,
    )
    display_name = fields.Char(
        string="Label",
        required=True,
    )
    description = fields.Text()
    is_required = fields.Boolean()
    value = fields.Char()
    value_default = fields.Char()
    version_id = fields.Many2one(
        string='Version',
        comodel_name='infrastructure.application.version',
        ondelete='cascade',
        required=True,
    )
