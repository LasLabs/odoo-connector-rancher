# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureConnector(models.AbstractModel):
    """This represents a connection to a remote infrastructure service."""

    _name = 'infrastructure.connector'
    _description = 'Infrastructure Connector'

    environment_ids = fields.Many2many(
        string='Environments',
        comodel_name='infrastructure.environment',
        compute='_compute_environment_ids',
    )

    @api.multi
    def _compute_environment_ids(self):
        for record in self:
            environments = self.env['infrastructure.environment'].search([
                ('reference', '=', '%s,%s' % (record._name, record.id)),
            ])
            record.environment_ids = [(6, 0, environments.ids)]

    @api.multi
    def deploy_application(self, wizard):
        """This deploys an application according to wizard options.

        Connectors should implement this for their contextual deploys.

        Args:
            wizard (InfrastructureApplicationDeploy): A completed deploy
                wizard representing an application deploy.

        Returns:
            InfrastructureStack: The new stack that was created.
        """
        raise NotImplementedError()
