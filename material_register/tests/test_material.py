from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.addons.material_register.tests.common import TestMaterialCommon


class TestMaterial(TestMaterialCommon):
    
    
    @classmethod
    def setUpClass(cls):
        super(TestMaterial, cls).setUpClass()
        cls.material = cls.env['material.register'].with_context(tracking_disable=True)

    def create_material(self, name,code,material_buy_price,material_type):
        return self.env['material.register'].create({
            'name': name,
            'material_code': code,
            'partner_id': self.partner_1.id,
            'material_buy_price': material_buy_price,
            'material_type': material_type,
            'currency_id': self.currency_id.id,
        })


    def test_set_material_write(self):
        material = self.env['material.register'].browse(self.material1.id)
        material.name = 'Kaos Oblong'
        self.assertEqual(self.material1, material)

    
    def test_set_material_constraint(self):
        with self.assertRaises(ValidationError):
            self.create_material(name="Kemeja",code='KMJ',material_buy_price=99,material_type='fabric')


    def test_set_material_unlink(self):
        material = self.env['material.register'].browse(self.material1.id)
        material_unlink = material.unlink()
        self.assertTrue(material_unlink)
    

