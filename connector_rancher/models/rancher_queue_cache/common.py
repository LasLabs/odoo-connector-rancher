# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RancherQueueCache(models.Model):
    """Caches the last time a record was imported.

    This helps to avoid duplicate lookups due to dependencies. Rancher does
    not have a concept of an updated date/time, so this is basically the only
    way to save some computational effort.
    """

    _name = 'rancher.queue.cache'
    _description = 'Rancher Queue Cache'

    backend_id = fields.Many2one(
        string='Backend',
        comodel_name='rancher.backend',
        required=True,
        ondelete='cascade',
    )
    model_name = fields.Char(
        required=True,
    )
    external_id = fields.Char(
        required=True,
    )
    date_check = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
    )
    date_expire = fields.Datetime(
        required=True,
    )

    def is_up_to_date(self, backend, model_name, external_id):
        """Check if there was a valid lookup recently."""
        return bool(
            self.search([
                ('backend_id', '=', backend.id),
                ('model_name', '=', model_name),
                ('external_id', '=', external_id),
                ('date_expire', '>=', fields.Datetime.now()),
            ])
        )
