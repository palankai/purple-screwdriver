from __future__ import print_function

import argparse
import logging

from openerp.cli import Command
from openerp.tools import config
import openerp.release
import openerp
import yaml

import purplespade
from .. import api


_logger = logging.getLogger(__name__)


class Screwdriver(Command):
    """Continous deployment tool"""

    def run(self, args):
        options, odooargs = self.parse_args(args)
        if options.scratch:
            purplespade.drop_database(options.database)

        actions = {
            'to remove': self._to_remove,
            'to install': self._to_install,
            'to upgrade': self._to_upgrade
        }
        purplespade.start_openerp(db_name=options.database, *odooargs)
        with purplespade.openerp_context() as env:
            self.update_module_list(env)
            modules = self.get_modules(env)
            builder = api.ActionPlanBuilder(
                system=self.get_module_information(env, modules),
                expected=self.get_expected_configuration(
                    options.screwdriver_file
                ),
            )
            action_plan = builder.build()
            for action in action_plan:
                actions[action.action](modules[action.name])
                env.cr.commit()
                env.clear()

    def update_module_list(self, env):
        res = env['ir.module.module'].update_list()
        if any(res):
            env.cr.commit()

    def get_modules(self, env):
        modules = {}
        for m in env['ir.module.module'].search([]):
            modules[m.name] = m
        return modules

    def get_module_information(self, env, modules):
        """
        Gives back the list of modules.
        Return:
            dict of api.ModuleState tuple
        """
        odoover = openerp.release.major_version
        result = {}
        for s in modules.values():
            is_outdated = s.state == 'installed' and \
                api.get_version(odoover, s.latest_version) != \
                api.get_version(odoover, s.installed_version)
            result[s['name']] = api.ModuleState(
                name=s['name'], is_outdated=is_outdated, state=s['state']
            )
        return result

    def get_expected_configuration(self, screwdriver_file):
        """
        Gives back the expected state of modules

        Return:
            dict of api.ModuleConfig
        """
        with(open(screwdriver_file)) as f:
            conf = yaml.load(f.read())
        modules = {}
        for name in conf['addons']:
            modules[name] = api.ModuleConfig(
                name=name, state=conf['addons'][name]
            )
        return modules

    def ensure_screwdriver(self, env):
        m = env['ir.module.module'].search(
            [('name', '=', 'purple_screwdriver')]
        )
        if m.state == 'uninstalled':
            self._to_install(m)
        if m.state == 'installed':
            self._to_upgrade(m)
        env.cr.commit()
        env.clear()

    def _to_remove(self, module):
        module.button_immediate_uninstall()
        _logger.info('Module %s  removed', module.name)

    def _to_install(self, module):
        module.button_immediate_install()
        _logger.info('Module %s is installed.', module.name)

    def _to_upgrade(self, module):
        module.button_immediate_upgrade()
        _logger.info('Module %s is upgraded', module.name)

    def get_parser(self):
        doc_paras = self.__doc__.split('\n\n')
        parser = argparse.ArgumentParser(
            description=doc_paras[0],
            prog="odoo-server screwdriver",
            epilog="You can also use any of openerp options",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            '-d', '--database', dest='database', default=config['db_name'],
            help="Build test database (default: %s)" % config['db_name']
        )
        parser.add_argument(
            '--scratch', dest='scratch', action='store_true',
            help="Recreate database before test"
        )
        parser.add_argument(
            '-f', '--file', dest='screwdriver_file', required=True,
            help='Screwdriver configuration'
        )
        return parser

    def parse_args(self, args):
        parser = self.get_parser()
        options, odooargs = parser.parse_known_args(args)
        if odooargs and odooargs[0] == '--':
            odooargs = odooargs[1:]
        return options, odooargs
