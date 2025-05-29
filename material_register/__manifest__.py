# -*- coding: utf-8 -*-
{
    'name': "Materials Register",

    'summary': """ 
        """,

    'description': """
        Module for material registration
    """,

    'author': "Siwi Wiyono Raharjo",
    'website': "https://www.linkedin.com/in/siwiyono",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/material_views.xml',
        'views/menu_items.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "application": True,
}
