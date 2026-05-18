{
    'name': 'Restrict Many2one Create/Edit',
    'version': '19.0.1.0.0',
    'category': 'Technical',
    'summary': 'Security group that globally restricts Create, Create & Edit, and Open/Edit on Many2one fields',
    'description': """
        Provides a dedicated security group "Restrict Many2one Create/Edit".
        Users assigned to this group cannot Create, Create & Edit, Quick Create,
        or Open/Edit records from any Many2one field anywhere in the system.

        Restriction is enforced at both the frontend (OWL/JS patching) and
        backend (Python validation) to prevent bypassing via direct RPC calls.
    """,
    'author': 'Custom',
    'depends': ['web'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'restrict_m2o_create_edit/static/src/js/many2one_restrict.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
