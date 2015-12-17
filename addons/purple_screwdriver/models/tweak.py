from openerp import models, fields


class Tweak(models.Model):
    _name = 'purple.screwdriver.tweak'

    name = fields.Char(string="Name", size=250, required=True)
