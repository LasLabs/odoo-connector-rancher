# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

from .constants import STATES_ACTIVE, STATES_HEALTH


class InfrastructureStack(models.Model):

    _name = 'infrastructure.stack'
    _description = 'Infrastructure Stacks'

    name = fields.Char(
        required=True,
    )
    description = fields.Char()
    environment_id = fields.Many2one(
        string='Environment',
        comodel_name='infrastructure.environment',
        required=True,
        ondelete='restrict',
    )
    application_version_id = fields.Many2one(
        string='Application Version',
        comodel_name='infrastructure.application.version',
    )
    service_ids = fields.One2many(
        string='Services',
        comodel_name='infrastructure.service',
        inverse_name='stack_id',
    )
    state = fields.Selection(
        selection=STATES_ACTIVE,
        default='inactive',
        required=True,
    )
    state_health = fields.Selection(
        selection=STATES_HEALTH,
    )
    is_system = fields.Boolean(
        help='This stack represents infrastructure services.',
    )
