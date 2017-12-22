# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# pylint: disable=C8101
{
    'name': 'Infrastructure',
    'summary': 'Provides models and methods required for connecting Odoo '
               'with infrastructure orchestration systems.',
    'version': '10.0.1.0.0',
    'category': 'Extra Tools',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs',
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'depends': [
        'product_uom_technology',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/infrastructure_application_view.xml',
        'views/infrastructure_environment_view.xml',
        'views/infrastructure_host_view.xml',
        'views/infrastructure_instance_view.xml',
        'views/infrastructure_option_view.xml',
        'views/infrastructure_option_system_view.xml',
        'views/infrastructure_service_view.xml',
        'views/infrastructure_stack_view.xml',
        'views/infrastructure_volume_view.xml',
        'views/infrastructure_volume_mount_view.xml',
        'wizards/infrastructure_application_deploy_view.xml',
        # Menu Last
        'views/infrastructure_menu.xml',
    ],
}
