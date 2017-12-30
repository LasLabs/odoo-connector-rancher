# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class RancherModelBinder(Component):
    """Bind records and give odoo/rancher ID relations."""

    _name = 'rancher.binder'
    _inherit = ['base.binder', 'base.rancher.connector']
    _apply_on = [
        'rancher.application',
        'rancher.application.version',
        'rancher.environment',
        'rancher.host',
        'rancher.instance',
        'rancher.service',
        'rancher.service.config',
        'rancher.stack',
        'rancher.volume',
    ]
