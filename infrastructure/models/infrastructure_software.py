# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureSoftware(models.Model):

    _name = 'infrastructure.software'
    _description = 'Infrastructure Software'

    name = fields.Char()
    description = fields.Char()
    type = fields.Selection([
        ('app', 'User Application'),
        ('kernel', 'Kernel'),
        ('os', 'Operating System'),
        ('server', 'Server Application'),
        ('virtualization', 'Virtualization Software'),
    ],
        default='app',
    )
    version_ids = fields.One2many(
        string='Versions',
        comodel_name='infrastructure.software.version',
        inverse_name='software_id',
    )
    license_ids = fields.One2many(
        string='Licenses',
        comodel_name='infrastructure.software.license',
        inverse_name='software_id',
    )

    _sql_constraints = [
        ('name_type_unique', 'UNIQUE(name, type)',
         'Software names must be unique per type.'),
    ]

    @api.model
    def create(self, vals):
        """Find an existing record of the same values, if existing."""
        software = self.search([
            ('name', '=', vals.get('name')),
            ('type', '=', vals.get('type', 'app')),
        ])
        if software:
            return software[:1]
        return super(InfrastructureSoftware, self).create(vals)
