# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import base64

from odoo import api, fields, models


class InfrastructureApplicationDeploy(models.TransientModel):
    """Wizard to facilitate the deploy of application templates."""

    _inherit = 'infrastructure.application.deploy'

    docker_compose = fields.Text(
        compute='_compute_docker_compose',
        inverse=lambda s: None,
        store=True,
    )
    rancher_compose = fields.Text(
        compute='_compute_rancher_compose',
        inverse=lambda s: None,
        store=True,
    )

    @api.multi
    @api.depends('version_id')
    def _compute_docker_compose(self):
        for record in self:
            attachment = record.version_id.get_file_by_name(
                'docker-compose.yml.tpl',
            )
            if not attachment:
                attachment = record.version_id.get_file_by_name(
                    'docker-compose.yml',
                )
            record.docker_compose = base64.b64decode(attachment.datas)

    @api.multi
    @api.depends('version_id')
    def _compute_rancher_compose(self):
        for record in self:
            attachment = record.version_id.get_file_by_name(
                'rancher-compose.yml',
            )
            record.rancher_compose = base64.b64decode(attachment.datas)
