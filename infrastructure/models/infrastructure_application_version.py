# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InfrastructureApplicationVersion(models.Model):

    _name = 'infrastructure.application.version'
    _description = 'Infrastructure Application Versions'

    application_id = fields.Many2one(
        string='Application',
        comodel_name='infrastructure.application',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        required=True,
    )
    file_ids = fields.Many2many(
        string='Files',
        comodel_name='ir.attachment',
        help='These are the files for application provisioning, such as a '
             '`docker-compose.yml` file.',
    )
    option_ids = fields.One2many(
        string='Options',
        comodel_name='infrastructure.application.option',
        inverse_name='version_id',
    )

    @api.multi
    @api.constrains('file_ids')
    def _check_file_ids_name(self):
        """Check for uniqueness in file names."""
        for record in self:
            seen_names = []
            for name in record.file_ids.mapped('name'):
                if name in seen_names:
                    raise ValidationError(_(
                        'File names must be unique per application version.',
                    ))
                seen_names.append(name)

    @api.multi
    def get_file_by_name(self, file_name):
        """Find the file in ``file_ids`` that matches the input name."""
        self.ensure_one()
        return self.file_ids.filtered(lambda r: r.name == file_name)
