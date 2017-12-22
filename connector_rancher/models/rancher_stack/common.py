# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.addons.component.core import Component


class InfrastructureStack(models.Model):

    _inherit = 'infrastructure.stack'

    rancher_bind_ids = fields.One2many(
        string='Rancher Bindings',
        comodel_name='rancher.stack',
        inverse_name='odoo_id',
    )


class RancherStack(models.Model):

    _name = 'rancher.stack'
    _inherit = 'rancher.binding'
    _inherits = {'infrastructure.stack': 'odoo_id'}
    _description = 'Rancher Stacks'

    _rec_name = 'name'

    odoo_id = fields.Many2one(
        string='Stack',
        comodel_name='infrastructure.stack',
        required=True,
        ondelete='cascade',
    )
    docker_compose = fields.Text()
    rancher_compose = fields.Text()
    answers = fields.Serialized(
        default={},
    )
    start_on_create = fields.Boolean()


class RancherStackAdapter(Component):
    """Utilize the API in context."""
    _name = 'rancher.stack.adapter'
    _inherit = 'rancher.adapter'
    _apply_on = 'rancher.stack'
    _rancher_endpoint = 'stack'

    def _switch_environment(self, environment_external_id):
        self.rancher._url = '%s/projects/%s/schemas' % (
            self.rancher._url, environment_external_id,
        )
        self.rancher.reload_schema()

    def create(self, values):
        self._switch_environment(values['accountId'])
        return super(RancherStackAdapter, self).create(values)

    def delete(self, _id):
        stack = self.env['rancher.stack'].search([
            ('backend_id', '=', self.backend_record.id),
            ('external_id', '=', _id),
        ])
        environment = stack.environment_id.rancher_bind_ids.filtered(
            lambda r: r.odoo_id == stack.environment_id
        )
        self._switch_environment(environment.external_id)
        super(RancherStackAdapter, self).delete(_id)
