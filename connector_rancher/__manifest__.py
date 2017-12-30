# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

# pylint: disable=C8101
{
    "name": "Rancher Connector",
    "summary": "Two way synchronization with Rancher",
    "version": "10.0.0.1.0",
    "category": "Connector",
    "website": "https://github.com/LasLabs/odoo-connector-rancher.git",
    "author": "LasLabs",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        'bin': ['envsubst'],
        "python": ['gdapi'],
    },
    "depends": [
        "connector",
        "infrastructure",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "security/ir.model.access.csv",
        "views/rancher_backend_view.xml",
        'wizards/infrastructure_application_deploy_view.xml',
        # Menu last
        "views/connector_menu.xml",
    ],
}
