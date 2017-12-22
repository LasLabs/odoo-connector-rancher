# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class InfrastructureApplication(models.Model):

    _name = 'infrastructure.application'
    _description = 'Infrastructure Applications'

    name = fields.Char(
        required=True,
    )
    description = fields.Char()
    default_version_id = fields.Many2one(
        string='Default Version',
        comodel_name='infrastructure.application.version',
        domain=[('id', 'in', 'version_ids')],
    )
    version_ids = fields.One2many(
        string='Versions',
        comodel_name='infrastructure.application.version',
        inverse_name='application_id',
    )
    label_ids = fields.Many2many(
        string='Labels',
        comodel_name='infrastructure.option',
    )
    category_ids = fields.Many2many(
        string='Categories',
        comodel_name='infrastructure.option',
        domain=[('name', '=', 'application.category')],
        context={'default_name': 'application.category'},
    )
    license = fields.Char()
    maintainer = fields.Char()
    is_system = fields.Boolean(
        help='This application installs infrastructure services.',
    )
