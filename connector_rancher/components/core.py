# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseRancherConnectorComponent(AbstractComponent):

    _name = 'base.rancher.connector'
    _inherit = 'base.connector'
    _collection = 'rancher.backend'
