import collections
import unittest

from .. import api


class TestActionPlanBuilder(unittest.TestCase):

    def test_when_an_unistalled_module_not_in_expected_list(self):
        system = {
            'sale': api.ModuleState('sale', 'uninstalled', is_outdated=False)
        }
        expected = {
        }
        builder = api.ActionPlanBuilder(
            system=system,
            expected=expected,
        )
        plan = builder.build()

        self.assertEqual(plan, [])

    def test_an_istalled_module_not_in_expected_list(self):
        system = {
            'sale': api.ModuleState('sale', 'installed', is_outdated=False)
        }
        expected = {
        }
        builder = api.ActionPlanBuilder(
            system=system,
            expected=expected,
        )
        plan = builder.build()

        self.assertEqual(plan, [])

    def test_an_istalled_module_have_to_be_removed(self):
        system = {
            'sale': api.ModuleState('sale', 'installed', is_outdated=False)
        }
        expected = {
            'sale': api.ModuleConfig('sale', 'removed')
        }
        builder = api.ActionPlanBuilder(
            system=system,
            expected=expected,
        )
        plan = builder.build()

        self.assertEqual(
            plan,
            [api.Action('sale', 'to remove')]
        )

    def test_an_unistalled_module_have_to_be_removed(self):
        system = {
            'sale': api.ModuleState('sale', 'uninstalled', is_outdated=False)
        }
        expected = {
            'sale': api.ModuleConfig('sale', 'removed')
        }
        builder = api.ActionPlanBuilder(
            system=system,
            expected=expected,
        )
        plan = builder.build()

        self.assertEqual(
            plan,
            []
        )

    def test_an_unistalled_module_have_to_be_installed(self):
        system = {
            'sale': api.ModuleState('sale', 'uninstalled', is_outdated=False)
        }
        expected = {
            'sale': api.ModuleConfig('sale', 'installed')
        }
        builder = api.ActionPlanBuilder(
            system=system,
            expected=expected,
        )
        plan = builder.build()

        self.assertEqual(
            plan,
            [api.Action('sale', 'to install')]
        )

    def test_an_istalled_module_have_to_be_installed(self):
        system = {
            'sale': api.ModuleState('sale', 'installed', is_outdated=False)
        }
        expected = {
            'sale': api.ModuleConfig('sale', 'installed')
        }
        builder = api.ActionPlanBuilder(
            system=system,
            expected=expected,
        )
        plan = builder.build()

        self.assertEqual(
            plan,
            []
        )

    def test_an_istalled_outdated_module_have_to_be_updated(self):
        system = {
            'sale': api.ModuleState('sale', 'installed', is_outdated=True)
        }
        expected = {
            'sale': api.ModuleConfig('sale', 'installed')
        }
        builder = api.ActionPlanBuilder(
            system=system,
            expected=expected,
        )
        plan = builder.build()

        self.assertEqual(
            plan,
            [api.Action('sale', 'to upgrade')]
        )

    def test_an_unistalled_module_have_to_be_updated(self):
        system = {
            'sale': api.ModuleState('sale', 'uninstalled', is_outdated=True)
        }
        expected = {
            'sale': api.ModuleConfig('sale', 'upgraded')
        }
        builder = api.ActionPlanBuilder(
            system=system,
            expected=expected,
        )
        plan = builder.build()

        self.assertEqual(
            plan,
            [api.Action('sale', 'to install')]
        )

    def test_an_istalled_module_have_to_be_updated(self):
        system = {
            'sale': api.ModuleState('sale', 'installed', is_outdated=False)
        }
        expected = {
            'sale': api.ModuleConfig('sale', 'upgraded')
        }
        builder = api.ActionPlanBuilder(
            system=system,
            expected=expected,
        )
        plan = builder.build()

        self.assertEqual(
            plan,
            [api.Action('sale', 'to upgrade')]
        )
