# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""
        UPDATE stock_picking
           SET inv_status = NULL
         WHERE COALESCE(is_standalone_delivery, FALSE) = FALSE
           AND inv_status IS NOT NULL
    """)
