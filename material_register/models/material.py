from odoo import _, api, fields, models
from odoo.osv import expression
from odoo.exceptions import ValidationError

class MaterialRegister(models.Model):
    _name = 'material.register'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Material Register'

    material_code = fields.Char('Material Code',required=True,tracking=True)
    name = fields.Char('Material Name',required=True,tracking=True)
    material_type = fields.Selection([
        ('fabric', 'Fabric'),
        ('jeans', 'Jeans'),
        ('cotton', 'Cotton'),
    ], string='Material Type',default="fabric",required=True,tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self: self.env.company.currency_id)
    material_buy_price = fields.Monetary('Material Buy Price',required=True,currency_field="currency_id",tracking=True)
    partner_id = fields.Many2one('res.partner', string='Related Partner',required=True,tracking=True)


    
    @api.constrains('material_buy_price')
    def _constrains_material_buy_price(self):
        for record in self:
            if record.material_buy_price < 100:
                raise ValidationError("Material Buy Price must be higher than 100")