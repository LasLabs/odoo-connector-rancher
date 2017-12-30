# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

from .constants import STATES_HEALTH


class InfrastructureEnvironment(models.Model):

    _name = 'infrastructure.environment'
    _description = 'Infrastructure Environments'

    name = fields.Char(
        required=True,
    )
    description = fields.Char()
    state = fields.Selection([
        ('active', 'Active'),
        ('deactivated', 'Deactivated'),
    ],
        default='deactivated',
    )
    state_health = fields.Selection(
        selection=STATES_HEALTH,
    )
    date_create = fields.Datetime(
        string='Create Date',
    )
    host_ids = fields.One2many(
        string='Hosts',
        comodel_name='infrastructure.host',
        inverse_name='environment_id',
    )
    company_ids = fields.Many2many(
        string='Companies',
        comodel_name='res.company',
        help='Users from these companies have access to the environment.',
    )
    connector = fields.Reference(
        selection=[],
        help='This is the reference to the connector that this environment '
             'is linked to. Connectors should add their backend model to '
             'this selection.',
    )

    @api.multi
    def name_get(self):
        names = []
        for record in self:
            name = record.name
            if record.connector:
                name += ' [%s]' % record.connector.name
            names.append((record.id, name))
        return names
