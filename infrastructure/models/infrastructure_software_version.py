# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureSoftwareVersion(models.Model):

    _name = 'infrastructure.software.version'
    _description = 'Infrastructure Software Versions'
    _inherits = {'infrastructure.software': 'software_id'}
    _rec_name = 'display_name'

    display_name = fields.Char(
        compute='_compute_display_name',
        store=True,
    )
    software_id = fields.Many2one(
        string='Software',
        comodel_name='infrastructure.software',
        required=True,
        ondelete='cascade',
    )
    license_ids = fields.Many2many(
        string='Licenses',
        comodel_name='infrastructure.software.license',
        domain="[('software_id', '=', software_id)]",
        context="{'default_software_id': software_id}",
        help='Software licenses that can apply to this version.',
        relation='infrastructure_software_license_version_rel',
    )
    version = fields.Char(
        help='Leave this blank for an unspecified version number.',
    )

    _sql_constraints = [
        ('software_id_version_unique', 'UNIQUE(software_id, version)',
         'This version already exists.'),
    ]

    @api.multi
    @api.depends('version')
    def _compute_display_name(self):
        for record in self:
            version = record.version and ' %s' % record.version or ''
            record.display_name = '%s%s' % (record.name, version)

    @api.multi
    def get_or_create(self, name, version, **additional_attributes):
        domain = [
            ('name', '=', name),
            ('version', '=', version),
        ]
        domain += [
            (key, '=', value) for key, value in additional_attributes.items()
        ]
        existing = self.search(domain)
        if existing:
            return existing[:1]
        values = {
            'name': name,
            'version': version,
        }
        values.update(additional_attributes)
        return self.create(values)
