from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.exceptions import UserError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestRemissionInvoicing(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.remission = cls.env['pos.remission'].create({
            'product_id': cls.product_a.id,
            'qty': 4.0,
            'pending_billing_qty': 4.0,
            'average_cost_amount': 10.0,
        })

    def _create_wizard(self, quantities, product=None):
        product = product if product is not None else self.product_a
        return self.env['pos.remission.wizard'].with_context(
            active_model='pos.remission',
            active_ids=self.remission.ids,
        ).create({
            'partner_id': self.partner_a.id,
            'line_ids': [Command.create({
                'product_id': product.id,
                'qty': quantity,
            }) for quantity in quantities],
        })

    def _create_invoice(self, quantities):
        action = self._create_wizard(quantities).action_create_account_move()
        return self.env['account.move'].browse(action['res_id'])

    def test_invoice_more_than_pending(self):
        invoice = self._create_invoice([6.0])
        self.assertEqual(invoice.state, 'draft')
        self.assertTrue(invoice.delivery_note_custom)
        self.assertEqual(invoice.invoice_line_ids.quantity, 6.0)
        self.assertEqual(self.remission.pending_billing_qty, 4.0)

        invoice.action_post()

        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(self.remission.pending_billing_qty, -2.0)
        self.assertEqual(self.remission.total_pending_billing, -20.0)
        self.assertEqual(self.remission.qty, 4.0)

    def test_invoice_less_than_pending(self):
        self._create_invoice([2.0]).action_post()
        self.assertEqual(self.remission.pending_billing_qty, 2.0)
        self.assertEqual(self.remission.total_pending_billing, 20.0)

    def test_invoice_with_zero_and_negative_balance(self):
        self._create_invoice([4.0]).action_post()
        self.assertEqual(self.remission.pending_billing_qty, 0.0)

        self._create_invoice([2.0]).action_post()
        self.assertEqual(self.remission.pending_billing_qty, -2.0)

        self._create_invoice([3.0]).action_post()
        self.assertEqual(self.remission.pending_billing_qty, -5.0)
        self.assertEqual(self.remission.total_pending_billing, -50.0)

    def test_repeated_product_lines_can_exceed_pending(self):
        self._create_invoice([4.0, 2.0]).action_post()
        self.assertEqual(self.remission.pending_billing_qty, -2.0)
        self.assertEqual(self.remission.total_pending_billing, -20.0)

    def test_wizard_requires_selected_product(self):
        wizard = self._create_wizard([1.0], product=self.product_b)
        with self.assertRaisesRegex(UserError, 'no pertenece a las remisiones seleccionadas'):
            wizard.action_create_account_move()

    def test_wizard_requires_lines(self):
        wizard = self._create_wizard([])
        with self.assertRaisesRegex(UserError, 'No hay productos'):
            wizard.action_create_account_move()

    def test_post_requires_existing_remission(self):
        invoice = self._create_invoice([6.0])
        self.remission.unlink()
        with self.assertRaisesRegex(UserError, 'No existe una remisión'), self.cr.savepoint():
            invoice.action_post()
        self.assertEqual(invoice.state, 'draft')

    def test_regular_invoice_does_not_change_remission(self):
        invoice = self._create_invoice([6.0])
        invoice.delivery_note_custom = False
        invoice.action_post()
        self.assertEqual(invoice.state, 'posted')
        self.assertEqual(self.remission.pending_billing_qty, 4.0)
