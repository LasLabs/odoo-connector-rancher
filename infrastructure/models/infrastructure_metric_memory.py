# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureMetricMemory(models.Model):

    _name = 'infrastructure.metric.memory'
    _description = 'Infrastructure Memory Metrics'
    _inherit = 'infrastructure.metric.abstract'

    memory_free = fields.Integer(
        readonly=True,
    )
    memory_cache = fields.Integer(
        readonly=True,
    )
    memory_buffer = fields.Integer(
        readonly=True,
    )
    memory_used = fields.Integer(
        readonly=True,
    )
    memory_total = fields.Integer(
        readonly=True,
    )
    memory_available = fields.Integer(
        readonly=True,
    )
    swap_cache = fields.Integer(
        readonly=True,
    )
    swap_free = fields.Integer(
        readonly=True,
    )
    swap_total = fields.Integer(
        readonly=True,
    )
    uom_id = fields.Many2one(
        string='Memory Units',
        comodel_name='product.uom',
        readonly=True,
        default=lambda s: s.env.ref(
            'product_uom_technology.product_uom_gib',
        ),
        domain="[('category_id.name', '=', 'Information')]",
        help='This unit represents all statistics for this record.',
    )

    @api.multi
    def name_get(self):
        names = []
        for record in self:
            name = '%s: %s total, %s free, %s used, %s buff/cache' % (
                record.uom_id.name,
                record.memory_total,
                record.memory_free,
                record.memory_used,
                record.memory_cache + record.memory_buffer,
            )
            names.append((record.id, name))
        return names
