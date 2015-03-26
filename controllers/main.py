from jinja2.loaders import BaseLoader
from datetime import datetime, date
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.web.controllers.main import content_disposition
__author__ = 'deimos'


class OdooTemplateLoader(BaseLoader):
    def __init__(self, model):
        self.model = model

    def get_source(self, environment, template):
        t = self.model.search([
            ('name', '=', template),
        ])
        return t.content, template, False

    def list_templates(self):
        templates = self.model.search([])
        return [template.filename for template in templates]


class DocumentController(http.Controller):

    #------------------------------------------------------
    # Document controllers
    #------------------------------------------------------
    @http.route([
        '/document/render/<template>',
        '/document/render/<template>/<model>/<docids>',
    ], type='http', auth='user')
    def document(self, template, model=None, docids='', **data):

        template_obj = request.env['document.template']
        target = template_obj.search([
            ('name', '=', template),
        ])

        model_obj = request.env[model] if model else False

        data.update({
            'objects': model_obj.browse([int(rec) for rec in docids.split(',')]) if model_obj is not False else [],
            'request': request,
            'target_model': model_obj
        })

        doc = target.render(data)

        httpheaders = [
            ('Content-Type', target.content_type),
            ('Content-Length', len(doc)),
            ('Content-Disposition', 'attachment; filename="{title}.{ext}"'.format(title=target.title, ext=target.extension))
        ]

        return request.make_response(doc, headers=httpheaders)

