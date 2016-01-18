from openerp import models, fields


class Addon(models.Model):
    _name = 'purple.screwdriver.config.addon'

    name = fields.Char(string="Name", size=250, required=True)
    state = fields.Char(string="State", size=30, required=True)
