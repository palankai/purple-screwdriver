from __future__ import print_function

import argparse
import glob
import importlib
import logging
import os
import sys
import textwrap

from openerp.cli import Command
from openerp.tools import config
import openerp.release
import yaml

import purplespade
from .. import api

_logger = logging.getLogger(__name__)

class Screwdriver(Command):
    """Continous deployment tool"""
    epilog="""
    """

    def run(self, args):
        options = self.parse_args(args)
        init = {}
        update = {}
        if options.scratch:
            purplespade.drop_database(options.database)
            init['screwdriver'] = 1
        else:
            update['screwdriver'] = 1

        actions = {
            'to remove': self._to_remove,
            'to install': self._to_install,
            'to update': self._to_update
        }

        with purplespade.openerp_env(
            db_name=options.database,
            without_demo=options.without_demo,
            init=init,
            update=update
        ) as env:
            modules = self.get_modules()
            action_plan = self.build_action_plan(
                env, options.conffile, modules
            )
            for action in action_plan:
                actions[action.action](modules[action.name])
            # TODO Store config changes!!!
            if action_plan:
                _logger.info('Appling %s modification', len(action_plan))
                upgrader = env['base.module.upgrade'].create({})
                env.cr.commit()
                upgrader.upgrade_module()
                _logger.info('Changes applied')
            else:
                _logger.info('No addon modification')

    def get_modules(self, env):
        modules = {}
        for m in env['ir.module.module'].search([]):
            modules[m.name] = m
        return modules

    def build_action_plan(self, env, conff, modules):
        builder = api.ActionPlan(
            system=self.get_module_information(env, modules),
            stored=self.get_module_configuration(env),
            expected=self.get_expected_configuration(env),
        )
        return builder.build()

    def get_module_information(self, env, modules):
        """
        Gives back the list of modules.
        Return:
            dict of api.ModuleState tuple
        """
        odoover = openerp.release.major_version
        modules = {}
        for s in modules.values():
            is_outdated = s.state == 'installed' and \
                api.get_version(odoover, s.latest_version) != \
                api.get_version(odoover, s.installed_version)
            modules[s['name']] = api.ModuleState(
                id=s.id, is_outdated=is_outdated, state=s['state']
            )
        return modules


    def get_module_configuration(self, env):
        """
        Gives back the stored configuration

        Return:
            dict of api.ModuleConfig tuple
        """
        stored = env['purple.screwdriver.config.addon'].read(['name', 'state'])
        modules = {}
        for s in stored:
            modules[s['name']] = api.ModuleConfig(
                id=s['id'], name=s['name'], state=s['state']
            )
        return modules

    def get_expected_configuration(self, conf_file):
        """
        Gives back the expected state of modules

        Return:
            dict of api.ModuleConfig
        """
        with(open(conf_file)) as f:
            conf = yaml.load(f.read())
        modules = {}
        for name in conf['addons']:
            modules[name] = api.ModuleConfig(
                id=None, name=name, state=conf['addons'][name]
            )
        return modules

    def _to_remove(self, module):
        module.state = 'to remove'
        _logger.info('Module %s marked to be removed', module.name)

    def _to_install(self, module):
        module.state_update(
            'to install', ['uninstalled']
        )
        _logger.info('Module %s marked to be installed', module.name)

    def _to_update(self, module):
        module.state_update(
            'to update', ['installed']
        )
        _logger.info('Module %s marked to be updated', module.name)

    def get_parser(self):
        doc_paras = self.__doc__.split('\n\n')
        parser = argparse.ArgumentParser(
            description=doc_paras[0],
            epilog=textwrap.dedent(self.epilog),
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
