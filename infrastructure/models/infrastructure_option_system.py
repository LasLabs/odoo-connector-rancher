# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureOptionSystem(models.Model):

    _name = 'infrastructure.option.system'
    _inherit = 'infrastructure.option'
    _description = 'Infrastructure System Options'

    value_2 = fields.Char(
        help='Sometimes there is a second value, such as permissions.',
    )
    value_2_join = fields.Char(
        default=':',
        help='If there is a ``value_2``, this will be used to join it with '
             'the existing values.',
    )

    @api.model
    def get_or_create(self, name, value=False, value_2=False,
                      value_2_join=':'):
        return super(InfrastructureOptionSystem, self).get_or_create(
            name=name,
            value=value,
            value_2=value_2,
            value_2_join=value_2_join,
        )

    @api.multi
    def name_get(self):
        results = []
        for record in self:
            name = '%s:%s' % (record.name, record.value)
            if record.value_2:
                name += '%s%s' % (record.value_2_join, record.value_2)
            results.append((record.id, name))
        return results
