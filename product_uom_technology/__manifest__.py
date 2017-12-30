# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

# pylint: disable=C8101
{
    'name': 'Product UoM - Technology',
    'summary': 'Adds technology related units of measure, such as '
               'informational units like gigabyte.',
    'version': '10.0.1.0.0',
    'category': 'Extra Tools',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'product',
    ],
    'data': [
        'data/product_uom_categ_data.xml',
        'data/product_uom_data.xml',
    ],
}
