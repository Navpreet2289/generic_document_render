import base64
from types import MethodType
import re
import mimetypes
from openerp import models, fields, api, _


__author__ = 'deimos'

mimetypes.init()

TYPE_RE = re.compile('_render_\w[\w_]+')


def get_types(model):
    return [
        (attr.replace('_render_', ''), attr.replace('_render_', '').capitalize()) for attr in dir(model)
        if TYPE_RE.match(attr) and isinstance(getattr(model, attr), MethodType)
    ]


class DocumentTemplate(models.Model):
    _name = 'document.template'

    name = fields.Char('Document', required=True)
    extension = fields.Char('Extension', compute='_compute_extension')

    title = fields.Char('Title', required=True, translate=True)
    content_type = fields.Char('Content Type', compute='_compute_extension')
    content = fields.Text('Content', required=True)
    file = fields.Binary('File')
    type = fields.Selection(selection='_get_type_selection', string='Render', required=True)

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'The name must be unique.')
    ]

    _order = 'name'

    @api.model
    def _get_type_selection(self):
        return get_types(self)

    @api.one
    @api.onchange('name')
    def _compute_extension(self):
        self.extension = self.name.split('.')[-1] if self.name else ''
        self.content_type = mimetypes.types_map.get('.' + self.extension, 'application/octet-stream')

    @api.one
    @api.constrains('name')
    def _check_name(self):
        if not re.match('[\w\d]+\.[\w\d]+(\.[\w\d]+)*', self.name):
            raise ValueError(_("Name is not valid."))

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        f = vals.get('file')
        if f:
            vals.update({
                'content': base64.decodestring(f),
                'file': False
            })

        return super(DocumentTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        f = vals.get('file')
        if f:
            vals.update({
                'content': base64.decodestring(f),
                'file': False
            })

        return super(DocumentTemplate, self).write(vals)

    @api.multi
    def render(self, data, **params):
        method_name = "_render_{type}".format(type=self.type)
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(data, **params)

    @api.model
    def render_template(self, template, data=None, **params):
        tmp = self.search([('name', '=', template)])
        if tmp:
            return tmp.render(data if data else {}, **params)
        return None