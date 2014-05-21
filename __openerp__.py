# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Product cost price',
    'version': '1.0',
    'category': 'Accounting & Finance',
    'sequence': 100,
    'summary': 'Adds product cost price computation',
    'description': """
Product cost price computation
==================================

Calculate the cost of imported goods in transit operations:
----------------------------------------------------------
    * Supplier invoice
    * Customs fees
    * Transit fees
    * Bank fees
    * Other fees

**Select purchase invoices** -> **Compute cost price** -> **Update product standard price**
    """,
    'author': 'NEXTMA SARL',
    'website': 'http://www.nextma.ma',
    'depends': ['base', 'product', 'account'],
    'images': ['images/business_form.png',],
    'data': [
        'security/transit_security.xml',
        'security/ir.model.access.csv',
        'transit_business_view.xml',
        'transit_business_sequence.xml'
    ],

    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
