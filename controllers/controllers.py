# -*- coding: utf-8 -*-
# from odoo import http


# class ProjectExcelReport(http.Controller):
#     @http.route('/project_excel_report/project_excel_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_excel_report/project_excel_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_excel_report.listing', {
#             'root': '/project_excel_report/project_excel_report',
#             'objects': http.request.env['project_excel_report.project_excel_report'].search([]),
#         })

#     @http.route('/project_excel_report/project_excel_report/objects/<model("project_excel_report.project_excel_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_excel_report.object', {
#             'object': obj
#         })
