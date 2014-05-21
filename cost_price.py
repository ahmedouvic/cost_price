from osv import osv, fields
import tools
import netsvc
import time
import pooler


class transit_business(osv.osv):
    _name = "transit.business"
    _description = "transit business"

    _columns = {
        'name': fields.char('Business', size=64, required=True),
        'code': fields.char('Business Number', size=64, required=True),
        'date_start': fields.date('Start Date'),
        'date_end': fields.date('End Date'),
        'coefficient': fields.float('Coefficient', readonly=True),
        'extra_costs': fields.float('Extra Costs',states={'confirmed':[('readonly',True)]}),
        'invoices': fields.one2many('account.invoice', 'business_id', 'Invoices'),
        'business_line': fields.one2many('transit.business.line', 'business_id', 'Product lines'),

        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled')
        ], 'State', select=2, readonly=True),
    }

    _defaults = {
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'transit.business'),
        'state': lambda * a: 'draft',
        'coefficient': lambda * a: 0,
    }

    def compute_all_lines(self, cr, uid, ids, context={}):
        pool = pooler.get_pool(cr.dbname)
        business_id = ids[0]
        business = pool.get('transit.business').browse(cr, uid, business_id)
        total_supplier = 0
        total_customs = 0
        total_transit = 0
        total_bank = 0
        total_others = business.extra_costs
        for invoice in business.invoices:
            if invoice.currency_id.rate==0:
                raise osv.except_osv(('Currency error'), ('Currency rate is null !'))
            amount_all = invoice.amount_total/invoice.currency_id.rate
            if invoice.purchase_type == 'supplier':
                total_supplier += amount_all
            elif invoice.purchase_type == 'transit':
                total_transit += amount_all
            elif invoice.purchase_type == 'customs':
                total_customs += amount_all
            elif invoice.purchase_type == 'bank':
                total_bank += amount_all
            else:
                total_others += amount_all
        total_costs = total_customs + total_transit + total_bank + total_others
        total_amount = total_supplier + total_customs + total_transit + total_bank + total_others
        try:
            total_coefficient = total_costs / total_supplier
            transit_coefficient = total_transit / total_supplier
            customs_coefficient = total_customs / total_supplier
            bank_coefficient = total_bank / total_supplier
            others_coefficient = total_others / total_supplier
        except ZeroDivisionError:
            raise osv.except_osv(('No supplier invoices'),
                                 ('A transit business must contains at least one supplier invoice'))

        sql = '''
        DELETE from transit_business_line where business_id = %s
        '''
        cr.execute(sql, (business_id,))
        for invoice in business.invoices:
            rate = invoice.currency_id.rate
            if invoice.purchase_type == 'supplier':
                for line in invoice.invoice_line:
                    price_unit = line.price_unit / rate
                    price_subtotal = line.price_subtotal / rate
                    product_line = {
                        'name': line.product_id.name,
                        'business_id': business_id,
                        'product_id': line.product_id.id,
                        'unit_price': price_unit,
                        'quantity': line.quantity,
                        'price_subtotal': price_subtotal,
                        'transit': price_subtotal*transit_coefficient,
                        'customs': price_subtotal*customs_coefficient,
                        'bank': price_subtotal*bank_coefficient,
                        'others': price_subtotal*others_coefficient,
                        'cost_price': price_unit*(1+total_coefficient)}
                    pool.get('transit.business.line').create(cr, uid, product_line)
        self.write(cr, uid, ids, {'coefficient': 1 + total_coefficient}, context=context)
        return True

    def draft_cb(self, cr, uid, ids, context=None):

        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def confirm_cb(self, cr, uid, ids, context=None):
        self.update_standard_price(cr, uid, ids)
        self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
        return True

    def cancel_cb(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancelled'}, context=context)

    def update_standard_price(self, cr, uid, ids, context={}):
        pool = pooler.get_pool(cr.dbname)
        business_id = ids[0]
        business = pool.get('transit.business').browse(cr, uid, business_id)
        product_obj = pool.get('product.product')

        for line in business.business_line :
            #sql = '''
            #    Update product_template set standard_price = %s Where id= %s
            #    '''
            #cr.execute(sql, (line.ps,line.product_id.id))
            product_obj.write(cr, uid, [line.product_id.id], {'standard_price': line.cost_price}, context=context)

transit_business()


class transit_business_line(osv.osv):
    _name = "transit.business.line"
    _description = "Product Lines"

    _columns = {
        'name': fields.char('Description', size=256, required=True),
        'business_id': fields.many2one('transit.business', 'Business Ref', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null'),
        'unit_price': fields.float('Unit_price',),
        'quantity': fields.float('Quantity',),
        'price_subtotal': fields.float('Subtotal',),
        'transit': fields.float('Transit',),
        'customs': fields.float('Customs',),
        'bank': fields.float('Bank'),
        'others': fields.float('Others'),
        'cost_price': fields.float('Cost price',)
    }

transit_business_line()


class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"
    _description = "invoice with transit business"
    _columns = {
        'business_id' : fields.many2one('transit.business', 'Business', required=False, readonly=True,
                                        states={'draft':[('readonly', False)]}),
        'purchase_type': fields.selection([
            ('supplier', 'Supplier invoice'),
            ('transit', 'Transit invoice'),
            ('customs', 'Customs invoice'),
            ('bank', 'Bank'),
            ('other', 'Other'),
            ], 'Purchase type', select=True, required=False, states={'draft':[('readonly', False)]}),
    }

    _defaults = {
        'purchase_type':lambda * a: 'supplier', }
account_invoice()