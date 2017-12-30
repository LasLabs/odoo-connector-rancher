# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InfrastructureApplicationDeploy(models.TransientModel):
    """Wizard to facilitate the deploy of application templates."""

    _name = 'infrastructure.application.deploy'
    _description = 'Deploy Infrastructure Applications'

    name = fields.Char(
        required=True,
    )
    description = fields.Char()
    environment_id = fields.Many2one(
        string='Environment',
        comodel_name='infrastructure.environment',
        required=True,
    )
    application_id = fields.Many2one(
        string='Application',
        comodel_name='infrastructure.application',
        readonly=True,
        default=lambda s: s._default_application_id(),
    )
    version_id = fields.Many2one(
        string='Version',
        comodel_name='infrastructure.application.version',
        default=lambda s: s._default_version_id(),
    )
    option_ids = fields.One2many(
        string='Options',
        comodel_name='infrastructure.deploy.option',
        inverse_name='deployer_id',
        compute='_compute_option_ids',
    )
    start_on_create = fields.Boolean(
        default=True,
        help='Should the services in the stack be started as soon as the '
             'stack is created?',
    )

    @api.model
    def _default_application_id(self):
        model = self.env['infrastructure.application']
        if self.env.context.get('active_model') != model._name:
            return
        return self.env.context.get('active_id')

    @api.model
    def _default_version_id(self):
        application = self.env['infrastructure.application'].browse(
            self._default_application_id(),
        )
        if not application:
            return
        return application.default_version_id.id

    @api.multi
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            stack_count = self.env['infrastructure.stack'].search_count([
                ('name', '=ilike', record.name),
                ('environment_id', '=', record.environment_id.id),
            ])
            if stack_count:
                raise ValidationError(_(
                    'There is already a stack by this name in this '
                    'environment. Note that stack name uniqueness is '
                    'not case sensitive.',
                ))

    @api.multi
    @api.depends('version_id.option_ids')
    def _compute_option_ids(self):
        for record in self:
            options = []
            for option in record.version_id.option_ids:
                option_values = dict(
                    option.copy_data()[0], value=option.value_default,
                )
                options.append((0, 0, option_values))
            record.option_ids = options

    @api.multi
    def action_deploy(self):
        """Calls ``deploy_application`` on the environment connector.

        Returns:

        """
        self.ensure_one()
        connector = self.environment_id.connector
        if not connector:
            raise ValidationError(_(
                'There is no connector linked to this environment.',
            ))
        return connector.deploy_application(self).get_formview_action()
