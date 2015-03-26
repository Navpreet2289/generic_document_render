from template import get_types
from openerp import models, fields, api, _
import types


__author__ = 'deimos'


class DocumentTemplateFunction(models.Model):
    _name = 'document.template.function'

    name = fields.Char('Name', required=True)
    code = fields.Text('Code', required=True)
    type = fields.Selection(selection='_get_type_selection', string='Render', required=True)

    @api.model
    def _get_type_selection(self):
        return get_types(self.env['document.template'])

    @api.one
    @api.constrains('code')
    def _check_code(self):
        try:
            l = eval(self.code)
            if not isinstance(l, types.LambdaType):
                raise ValueError(_("The python code must be a lambda."))
        except (SyntaxError, NameError, ):
            raise ValueError(_("The python code must be a lambda."))

    _sql_constraints = [
        ('name', 'unique(name)', 'The name must be unique')
    ]
