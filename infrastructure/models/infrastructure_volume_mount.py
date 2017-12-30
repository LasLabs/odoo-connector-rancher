# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureVolumeMount(models.Model):

    _name = 'infrastructure.volume.mount'
    _description = 'Infrastructure Volume Mount'

    display_name = fields.Char(
        compute='_compute_display_name',
    )
    instance_id = fields.Many2one(
        string='Instance',
        comodel_name='infrastructure.instance',
        required=True,
        ondelete='cascade',
    )
    volume_id = fields.Many2one(
        string='Volume',
        comodel_name='infrastructure.volume',
        required=True,
        ondelete='restrict',
    )
    path = fields.Char(
        required=True,
    )
    is_read_only = fields.Boolean(
        help='Is this volume mounted as read only?',
    )

    @api.multi
    @api.depends('path', 'volume_id.name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = '%s:%s' % (
                record.volume_id.name, record.path,
            )
