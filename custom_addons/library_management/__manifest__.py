# -*- coding: utf-8 -*-
{
    'name': "library_management",
    'summary': "Module for managing library books and loans",
    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",
    'category': 'Services/Library',
    'version': '0.1',
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/book_view.xml',
        'views/member_view.xml',
        'views/loan_view.xml',
        'views/menu.xml'
        
    ],
    'installable': True,
    'aplliaction': True,
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

