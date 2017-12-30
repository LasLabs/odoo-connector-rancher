# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models

from .constants import STATES_ACTIVE, STATES_HEALTH


class InfrastructureService(models.Model):

    _name = 'infrastructure.service'
    _description = 'Infrastructure Services'

    name = fields.Char(
        required=True,
    )
    description = fields.Char()
    state = fields.Selection(
        selection=STATES_ACTIVE,
        default='inactive',
    )
    stack_id = fields.Many2one(
        string='Stack',
        comodel_name='infrastructure.stack',
        ondelete='cascade',
    )
    environment_id = fields.Many2one(
        string='Environment',
        comodel_name='infrastructure.environment',
        ondelete='cascade',
    )
    company_ids = fields.Many2many(
        string='Companies',
        comodel_name='res.company',
        help='Users from these companies have access to the service and '
             'its instances. This will override environment permissions on '
             'instances.',
    )
    date_create = fields.Datetime(
        string='Creation Date',
        default=fields.Datetime.now,
    )
    scale_current = fields.Integer()
    scale_max = fields.Float(
        default=1,
    )
    state_health = fields.Selection(
        selection=STATES_HEALTH,
    )
    instance_ids = fields.One2many(
        string='Instances',
        comodel_name='infrastructure.instance',
        inverse_name='service_id',
    )
    config_id = fields.Many2one(
        string='Current Configuration',
        comodel_name='infrastructure.service.config',
        compute='_compute_config_id',
        store=True,
    )
    config_serialized = fields.Serialized(
        compute='_compute_config_serialized',
        inverse='_inverse_config_serialized',
    )
    config_ids = fields.One2many(
        string='All Configurations',
        inverse_name='service_id',
        comodel_name='infrastructure.service.config',
        domain=['|', ('active', '=', True), ('active', '=', False)],
    )

    @api.multi
    @api.depends('config_ids')
    def _compute_config_id(self):
        for record in self:
            record.config_id = record.config_ids[:1].id

    @api.multi
    @api.depends('config_id')
    def _compute_config_serialized(self):
        for record in self.filtered(lambda r: r.config_id):
            record.config_serialized = record.config_id.read()[0]

    @api.multi
    def _inverse_config_serialized(self):
        """Allow the saving of new configs based on input serialized data.

        This will not make any modifications if the serialized config is the
        same version as the saved config.
        """
        for record in self:
            serialized_version = record.config_serialized['version']
            if record.config_id.version != serialized_version:
                if record.config_id:
                    record.config_id.active = False
                record.config_ids = [(0, 0, record.config_serialized)]

    @api.multi
    def write(self, values):

        if not values.get('config_id'):
            return super(InfrastructureService, self).write(values)

        for record in self:
            if values['config_id'] != record.config_id.id:
                values['previous_config_id'] = record.config_id.id
            super(InfrastructureService, record).write(values)
