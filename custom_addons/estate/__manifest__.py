{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base'],
    'author': "Author Name",
    'category': 'Category',
    'application': True,
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_offer.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/res_users_views.xml',
        'report/estate_property_template.xml',
        'report/estate_property_reports.xml',
        'views/estate_menus.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        # 'demo/demo_data.xml',
    ],
}