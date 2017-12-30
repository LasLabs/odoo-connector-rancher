# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class InfrastructureMetricCpuCore(models.Model):

    _name = 'infrastructure.metric.cpu.core'
    _description = 'Infrastructure CPU Core Metrics'

    _rec_name = 'percent_use'

    cpu_metric_id = fields.Many2one(
        string='CPU Metric',
        comodel_name='infrastructure.metric.cpu',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    percent_use = fields.Float(
        readonly=True,
    )
