from __future__ import print_function

import argparse
import logging

from openerp.cli import Command
from openerp.tools import config
import openerp.release
import yaml

import purplespade
from .. import api


_logger = logging.getLogger(__name__)


class Screwdriver(Command):
    """Continous deployment tool"""

    def run(self, args):
        options = self.parse_args(args)
        if options.scratch:
            purplespade.drop_database(options.database)

        actions = {
            'to remove': self._to_remove,
            'to install': self._to_install,
            'to upgrade': self._to_upgrade
        }
        with purplespade.openerp_env(
            db_name=options.database,
            without_demo=options.without_demo,
        ) as env:
            modules = self.get_modules(env)
            builder = api.ActionPlanBuilder(
                system=self.get_module_information(env, modules),
                expected=self.get_expected_configuration(options.conffile),
            )
            action_plan = builder.build()
            for action in action_plan:
                actions[action.action](modules[action.name])
                env.cr.commit()
                env.clear()

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

    def get_expected_configuration(self, conf_file):
        """
        Gives back the expected state of modules

        Return:
            dict of api.ModuleConfig
        """
        with(open(conf_file)) as f:
            conf = yaml.load(f.read())[0]
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
        _logger.info('Module %s marked to be upgrade', module.name)

    def get_parser(self):
        doc_paras = self.__doc__.split('\n\n')
        parser = argparse.ArgumentParser(
            description=doc_paras[0],
            prog="odoo-server screwdriver",
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
            '--without-demo', dest='without_demo',
            default='all',
            help="""disable loading demo data for modules to be installed
                (comma-separated, use "all" for all modules)
                By default loads demo data """
        )
        parser.add_argument(
            '-c', '--conf', dest='conffile', required=True,
            help='Screwdriver configuration'
        )
        return parser

    def parse_args(self, args):
        parser = self.get_parser()
        options = parser.parse_args(args)
        return options
