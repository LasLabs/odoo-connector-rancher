# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureSoftwareLicense(models.Model):

    _name = 'infrastructure.software.license'
    _description = 'Infrastructure Software Licenses'

    name = fields.Char(
        sting='Key',
        required=True,
    )
    is_valid = fields.Boolean(
        compute='_compute_is_valid',
    )
    valid_start = fields.Date(
        string='Valid On',
        help='License is activated on this date.',
    )
    valid_end = fields.Date(
        string='Valid Until',
        help='License expires on this date.',
    )
    install_max = fields.Integer(
        string='Max Installs'
    )
    software_id = fields.Many2one(
        string='Software',
        comodel_name='infrastructure.software',
        required=True,
        ondelete='restrict',
    )
    version_ids = fields.Many2many(
        string='Versions',
        comodel_name='infrastructure.software.version',
        domain="[('software_id', '=', software_id)]",
        context="{'default_software_id': software_id}",
        help='Software versions this license can apply to.',
        relation='infrastructure_software_license_version_rel',
    )

    @api.multi
    @api.depends('valid_start', 'valid_end')
    def _compute_is_valid(self):
        date_today = fields.Date.today()
        for record in self:
            record.is_valid = \
                record.valid_start <= date_today <= record.valid_end
