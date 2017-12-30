# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureOption(models.Model):

    _name = 'infrastructure.option'
    _description = 'Infrastructure Options'

    name = fields.Char(
        required=True,
    )
    value = fields.Char()

    @api.multi
    def name_get(self):
        return [
            (n.id, '%s: "%s"' % (n.name, n.value)) for n in self
        ]

    @api.model
    def get_or_create_bulk(self, iterator):
        """Get/create in bulk. Iterator lines feed to ``get_or_create``."""
        results = self
        for i in iterator:
            try:
                results += self.get_or_create(**i)
            except TypeError:
                results += self.get_or_create(*i)
        return results

    @api.model
    def get_or_create(self, name, value=False, **others):
        """Return an existing or new option matching ``name`` and ``value``.
        """
        domain = [
            ('name', '=', name),
            ('value', '=', value),
        ]
        domain += [(k, '=', v) for k, v in others.items()]
        option = self.search(domain)
        if option:
            return option[:1]
        values = {
            'name': name,
            'value': value,
        }
        values.update(others)
        return self.create(values)
