# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

from .constants import STATES_ACTIVE


class InfrastructureVolume(models.Model):

    _name = 'infrastructure.volume'
    _description = 'Infrastructure Volumes'

    name = fields.Char(
        required=True,
    )
    type = fields.Selection([
        ('file_system', 'File System'),
        ('volume', 'Volume')
    ],
        default='volume',
        readonly=True,
    )
    external_name = fields.Char(
        help='This is the name of the volume according to the volume driver.',
    )
    state = fields.Selection(
        selection=STATES_ACTIVE,
        default='inactive',
    )
    access_mode = fields.Char()
    driver = fields.Char()
    driver_option_ids = fields.Many2many(
        string='Driver Options',
        comodel_name='infrastructure.option',
    )
    environment_id = fields.Many2one(
        string='Environment',
        comodel_name='infrastructure.environment',
        required=True,
    )
    host_id = fields.Many2one(
        string='Host',
        comodel_name='infrastructure.host',
    )
    is_host_path = fields.Boolean(
        help='This indicates that the volume is located directly on the host.',
    )
    mount_ids = fields.One2many(
        string='Mounts',
        comodel_name='infrastructure.volume.mount',
        inverse_name='volume_id',
    )
    capacity = fields.Float()
    capacity_uom_id = fields.Many2one(
        string='Capacity Units',
        comodel_name='product.uom',
        default=lambda s: s.env.ref(
            'product_uom_technology.product_uom_gib',
        ),
        domain="[('category_id.name', '=', 'Information')]",
    )

    _sql_constraints = [
        ('host_name_unique', 'UNIQUE(host_id, name)',
         'This volume already exists on this host.'),
    ]

    @api.model
    def get_or_create(self, name, host=None, environment=None, **additional):
        """Get existing or create new volume according to input."""
        host_id = host and host.id or False
        environment_id = environment and environment.id or False
        if not environment_id and host:
            environment_id = host.environment_id.id
        domain = [
            ('name', '=', name),
            ('host_id', '=', host_id),
            ('environment_id', '=', environment_id)
        ]
        domain += [(k, '=', v) for k, v in additional.items()]
        volume = self.search(domain)
        if volume:
            return volume[:1]
        values = {
            'name': name,
            'host_id': host_id,
            'environment_id': environment_id,
        }
        values.update(additional)
        return self.create(values)
