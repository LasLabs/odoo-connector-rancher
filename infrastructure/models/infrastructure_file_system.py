# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureFileSystem(models.Model):

    _name = 'infrastructure.file.system'
    _description = 'Infrastructure File System'
    _inherits = {'infrastructure.volume': 'volume_id'}

    metric_id = fields.Many2one(
        string='Last Metric',
        comodel_name='infrastructure.metric.storage',
        compute='_compute_metric_id',
        inverse='_inverse_metric_id',
    )
    metric_ids = fields.Many2many(
        string='Metrics',
        comodel_name='infrastructure.metric.storage',
    )
    volume_id = fields.Many2one(
        string='Volume',
        comodel_name='infrastructure.volume',
        required=True,
        ondelete='restrict',
    )

    _sql_constraints = [
        ('volume_unique', 'UNIQUE(volume_id)',
         'A file system is already mapped to this volume.'),
    ]

    @api.multi
    def _compute_metric_id(self):
        for record in self:
            record.metric_id = record.metric_ids[:1].id

    @api.multi
    def _inverse_metric_id(self):
        for record in self:
            if record.cpu_metric_id:
                record.metric_id.reference = record
                record.metric_ids = [(4, record.metric_id.id)]

    @api.model
    def get_or_create(self, name, host, **additional):
        additional['type'] = 'file_system'
        volume = self.env['infrastructure.volume'].get_or_create(
            name, host, **additional
        )
        file_system = self.search([('volume_id', '=', volume.id)])
        if file_system:
            return file_system[:1]
        return self.create({
            'volume_id': volume.id,
        })
