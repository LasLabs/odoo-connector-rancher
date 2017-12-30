# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from contextlib import contextmanager

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    import gdapi
except ImportError:
    _logger.info('`gdapi-python` is not installed.')


class RancherBackend(models.Model):

    _name = 'rancher.backend'
    _description = 'Rancher Backend'
    _inherit = ['connector.backend',
                'infrastructure.connector',
                ]

    name = fields.Char(
        required=True,
    )
    version = fields.Selection(
        selection='_get_versions',
        default='v2-beta',
        required=True,
    )
    catalog_version = fields.Selection(
        selection='_get_catalog_versions',
        default='v1-catalog',
        required=True,
    )
    access_key = fields.Char(
        required=True,
    )
    secret_path = fields.Char(
        required=True,
        default='/run/secrets/rancher_secret',
        help='This is the path to the secrets file that contains the '
             'secret key for connecting to Rancher.',
    )
    host = fields.Char(
        required=True,
    )
    port = fields.Integer(
        required=True,
        default=8080,
    )
    is_ssl = fields.Boolean()
    active = fields.Boolean(
        default=True,
    )
    company_ids = fields.Many2many(
        string='Companies',
        comodel_name='res.company',
        default=lambda s: [(6, 0, s.env.user.company_id.ids)],
    )
    cache_minutes = fields.Integer(
        default=5,
        required=True,
        help='Amount of minutes that a record is considered up to date. '
             'Rancher does not have a real way to identify updated records, '
             'so this is mechanism prevents higher level records (such as '
             'hosts) from being overly imported due to being in the '
             'dependency chains.',
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'This name is already used.'),
    ]

    @api.model
    def _get_versions(self):
        """Available versions for this backend."""
        return [('v2-beta', 'v2')]

    @api.model
    def _get_catalog_versions(self):
        return [('v1-catalog', 'v1')]

    @api.multi
    def action_sync_all(self):
        """Queue a sync of all instances and applications from Rancher."""
        for backend in self:
            self.env['rancher.application'].with_delay().import_batch(backend)
            self.env['rancher.instance'].with_delay().import_batch(backend)

    @api.multi
    def deploy_application(self, wizard):
        """Create a new stack based on the application."""
        self.ensure_one()
        rancher_stack = self.env['rancher.stack'].create({
            'backend_id': self.id,
            'name': wizard.name,
            'description': wizard.description,
            'environment_id': wizard.environment_id.id,
            'application_version_id': wizard.version_id.id,
            'docker_compose': wizard.docker_compose,
            'rancher_compose': wizard.rancher_compose,
            'start_on_create': wizard.start_on_create,
            'is_system': wizard.application_id.is_system,
            'answers': {
                o.name: o.value for o in wizard.option_ids if o.value
            },
        })
        return rancher_stack.odoo_id

    @api.multi
    def get_client(self, use_catalog_api=False):
        self.ensure_one()
        scheme = 'https' if self.is_ssl else 'http'
        with open(self.secret_path, 'r') as fh:
            secret_key = fh.read().strip()
        version = self.catalog_version if use_catalog_api else self.version
        return gdapi.Client(
            url='%s://%s:%s/%s' % (
                scheme, self.host, self.port, version,
            ),
            access_key=self.access_key,
            secret_key=secret_key,
        )

    @api.multi
    def test_connection(self):
        for record in self:
            record.get_client()
        raise ValidationError(_('Connection successful.'))

    @api.multi
    @contextmanager
    def work_on(self, model_name, **kwargs):
        """Context manager providing a usable API for external access.

        Yields:
            odoo.addons.component.core.WorkContext: The worker context for
                this backend record. The ``Rancher`` object is exposed on
                the ``rancher_api`` attribute of this context.
        """
        self.ensure_one()
        use_catalog_api = self.env[model_name].USE_CATALOG_API
        rancher_api = self.get_client(use_catalog_api)
        # From the components, we can do ``self.work.rancher_api``
        with super(RancherBackend, self).work_on(
            model_name, rancher_api=rancher_api, **kwargs
        ) as work:
            yield work

    @api.model
    def _cron_get_remote_records(self, model_name):
        """Use this cron to get all objects of a certain type from Rancher.

        This is how new objects are identified, but old objects are also
        updated.
        """
        for backend in self.search([]):
            self.env[model_name].import_batch(backend)
