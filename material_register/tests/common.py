# -*- coding: utf-8 -*-

from odoo.tests import common


class TestMaterialCommon(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestMaterialCommon, cls).setUpClass()

        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Julia Agrolait',
            'email': 'julia@agrolait.example.com',
        })
        cls.currency_id = cls.env['res.currency'].search([('name', '=', 'IDR')])

        cls.material1 = cls.env['material.register'].create({
            'name': 'Kaos',
            'material_code' : 'KS',
            'material_type' : 'fabric',
            'material_buy_price' : 100000,
            'partner_id': cls.partner_1.id,
            'currency_id': cls.currency_id.id
        })