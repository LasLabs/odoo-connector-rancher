# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureInstance(models.Model):

    _name = 'infrastructure.instance'
    _inherits = {'infrastructure.service': 'service_id',
                 'infrastructure.service.config': 'config_id',
                 }
    _description = 'Infrastructure Instances'

    service_id = fields.Many2one(
        string='Service',
        comodel_name='infrastructure.service',
        ondelete='cascade',
    )
    mount_ids = fields.One2many(
        string='Mounts',
        comodel_name='infrastructure.volume.mount',
        inverse_name='instance_id',
    )
    host_id = fields.Many2one(
        string='Host',
        comodel_name='infrastructure.host',
        required=True,
    )
    company_ids = fields.Many2many(
        string='Companies',
        comodel_name='res.company',
        compute='_compute_company_ids',
        help='Users from these companies have access to the service and '
             'its instances.',
    )

    @api.multi
    @api.depends('host_id.environment_id.company_ids',
                 'service_id.company_ids',
                 )
    def _compute_company_ids(self):
        """Use the service companies if defined, otherwise environment."""
        for record in self:
            company_service = record.service_id.company_ids
            company_environment = record.host_id.environment_id.company_ids
            record.company_ids = [
                (6, 0, company_service.ids or company_environment.ids),
            ]
