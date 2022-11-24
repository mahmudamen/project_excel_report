# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
from odoo import tools
import xlwt
from io import BytesIO
from xlsxwriter.workbook import Workbook

import base64



class projectexcelreport(models.Model):
    _name = 'project.excel.report'
    _auto = False

    project_id = fields.Many2one('project.project', string='project' )
    budget = fields.Float("Budget")
    ctd = fields.Float("CTD")
    saleorder = fields.Float("Sale Order")
    invoicedamount = fields.Float("Invoiced Amount")
    revenuetodate = fields.Float("Revenue to Date")
    margin = fields.Float("Margin")
    ofcompletion = fields.Float("% Of Completion")
    project_file = fields.Char('Name', size=256)
    file_name = fields.Binary('project_file', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')





    def init(self):
        tools.drop_view_if_exists(self._cr, 'project_excel_report')
        self._cr.execute("""
        create or replace view project_excel_report as (
        select  row_number() OVER () as id, project.id as project_id ,
            ( select sum(budget.planned_amount) from crossovered_budget_lines budget where project.analytic_account_id = budget.analytic_account_id)   as budget ,
            ( select sum(analytic.amount) from account_analytic_line analytic where project.id = analytic.project_id and analytic.timesheet_invoice_type = 'other_costs')  as ctd ,
            ( select sum(sale.amount_total) from sale_order sale where project.id = sale.project_id)  as saleorder ,
            ( select sum(saleorderline.price_total) from sale_order_line saleorderline where project.id = saleorderline.project_id) as invoicedamount ,
            ( select sum(projectprofitability.amount_untaxed_invoiced) + sum(projectprofitability.amount_untaxed_to_invoice) + sum(projectprofitability.expense_amount_untaxed_invoiced) + sum(projectprofitability.expense_amount_untaxed_to_invoice) + sum(projectprofitability.other_revenues) from project_profitability_report projectprofitability where project.id = projectprofitability.project_id ) as revenuetodate ,
            ( select sum(projectprofitability.margin) from project_profitability_report projectprofitability where project.id = projectprofitability.project_id) as margin ,
            ( select sum(projecttask.hours_effective)*100/sum(projecttask.hours_planned) from report_project_task_user projecttask where project.id = projecttask.project_id) as ofcompletion 
            from project_project project 
                            )""")

    def project_excel_report(self):
        return {
            'name': _('Wizard String'),
            'type': 'ir.actions.act_window',
            'res_model': 'project.excel.report.xls',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',

        }

class project_excel_report(models.TransientModel):
    _name = "project.excel.report.xls"

    project_id = fields.Many2one('project.project', string='project' )
    budget = fields.Float("Budget")
    ctd = fields.Float("CTD")
    saleorder = fields.Float("Sale Order")
    invoicedamount = fields.Float("Invoiced Amount")
    revenuetodate = fields.Float("Revenue to Date")
    margin = fields.Float("Margin")
    ofcompletion = fields.Float("% Of Completion")
    project_file = fields.Char('Name', size=256)
    file_name = fields.Binary('project_file', readonly=True)
    state = fields.Selection([('choose', 'choose'), ('get', 'get')],
                             default='choose')

    def project_excel_report(self):
        file_name = 'project_file.xls'
        query = """ 
                    select    project.name as project_id ,
                        ( select sum(budget.planned_amount) from crossovered_budget_lines budget where project.analytic_account_id = budget.analytic_account_id)   as budget ,
                        ( select sum(analytic.amount) from account_analytic_line analytic where project.id = analytic.project_id and analytic.timesheet_invoice_type = 'other_costs')  as ctd ,
                        ( select sum(sale.amount_total) from sale_order sale where project.id = sale.project_id)  as saleorder ,
                        ( select sum(saleorderline.price_total) from sale_order_line saleorderline where project.id = saleorderline.project_id) as invoicedamount ,
                        ( select sum(projectprofitability.amount_untaxed_invoiced) + sum(projectprofitability.amount_untaxed_to_invoice) + sum(projectprofitability.expense_amount_untaxed_invoiced) + sum(projectprofitability.expense_amount_untaxed_to_invoice) + sum(projectprofitability.other_revenues) from project_profitability_report projectprofitability where project.id = projectprofitability.project_id ) as revenuetodate ,
                        ( select sum(projectprofitability.margin) from project_profitability_report projectprofitability where project.id = projectprofitability.project_id) as margin ,
                        ( select sum(projecttask.hours_effective)*100/sum(projecttask.hours_planned) from report_project_task_user projecttask where project.id = projecttask.project_id) as ofcompletion 
                        from project_project project
                    """
        self.env.cr.execute(query)
        workbook = xlwt.Workbook(encoding="UTF-8")
        sheet = workbook.add_sheet("project excel report")

        format1 = xlwt.easyxf('font:bold True;pattern: pattern solid, fore_colour gray25;align: horiz left')
        sheet.write(2, 0, 'project', format1)
        sheet.write(2, 1, 'budget', format1)
        sheet.write(2, 2, 'CTD', format1)
        sheet.write(2, 3, 'Sale Order', format1)
        sheet.write(2, 4, 'Invoiced Amount', format1)
        sheet.write(2, 5, 'Revenue to Date', format1)
        sheet.write(2, 6, 'Margin', format1)
        sheet.write(2, 7, '% Of Completion', format1)

        data = self.env.cr.fetchall()
        x = 0
        for row in range(len(data)):
            h = 0
            for i in data[row]:

                sheet.write(x + 3, h, i, format1)
                h = 1 + h
            x = 1 +x




        for name in data:
            workbook.add_sheet(name[0])
        for n, datas in enumerate(list(data)):
            ws = workbook.get_sheet(n+1)
            x = 0
            h = 0
            ws.write(2, 0, 'project', format1)
            ws.write(2, 1, 'budget', format1)
            ws.write(2, 2, 'CTD', format1)
            ws.write(2, 3, 'Sale Order', format1)
            ws.write(2, 4, 'Invoiced Amount', format1)
            ws.write(2, 5, 'Revenue to Date', format1)
            ws.write(2, 6, 'Margin', format1)
            ws.write(2, 7, '% Of Completion', format1)
            for i in datas:

                ws.write(x + 3, h, i, format1)
                h = 1 + h
            x = 1 + x


        fp = BytesIO()
        workbook.save(fp)
        self.write(
            {'state': 'get', 'file_name': base64.encodestring(fp.getvalue()), 'project_file': file_name})
        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.excel.report.xls',
            'view_mode': 'form',
            'view_type':'form',
            'res_id': self.id,
            'target': 'new',
        }