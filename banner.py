from odoo import fields, models, api,_
from PIL import Image
import io
import base64
from odoo.exceptions import ValidationError


class banner_image(models.Model):
    _name = 'banner.image'

    name = fields.Char(string="Name", required=True)
    title = fields.Char(string="Title", size=30)
    description = fields.Text(string="Description", size=300)
    link = fields.Char(string="Read More Link", widget="url")
    tags = fields.Many2many('res.partner.category', string="Tags")
    sequence = fields.Integer(string="Sequence")
    state = fields.Selection(string='',
                             selection=[('draft', 'Draft'),
                                        ('archived', 'Archived'),
                                        ('published', 'Published')],
                                        default='draft')
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')
    tag_count = fields.Integer(compute='_compute_tag_count', string="No. of tags attached")
    image = fields.Binary("Image", attachment=True)

    def get_image_dimensions(self,image):
        """
        Helper function that returns the image dimentions :param: imagefile str (path to image)
        :return dict (of the form: {width:<int>, height=<int>, size_bytes=<size_bytes>)
        """
        # Inline import for PIL because it is not a common library
        get_image = base64.b64decode(image)
        img = Image.open(io.BytesIO(get_image))
        width, height = img.size
        if width > 1200:
            raise ValidationError(_('Image Cant Be Gatter Than 1200px'))
        return dict(width=width, height=height, size_bytes=0)

    @api.model
    def create(self, vals):
        img = vals['image']
        self.get_image_dimensions(img)
        return  super(banner_image, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'active' in vals:
            if vals['active']:
                vals['state'] = 'draft'
            else:
                vals['state'] = 'archived'


        if 'image' in vals:
            img = vals['image']
            self.get_image_dimensions(img)
        return super(banner_image,self).write(vals)


    @api.multi
    def action_confirm(self):
        return self.write({'state': 'published'})

    @api.multi
    def action_validate(self):
        self.write({'state': 'archived'})
        return True

    @api.multi
    def action_reset(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def _compute_tag_count(self):
        for res in self:
            res.tag_count = len(res.tags)


