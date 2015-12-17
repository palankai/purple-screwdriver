import unittest

from .. import api


class TestToDo(unittest.TestCase):

    def test_version_exception(self):
        with self.assertRaises(Exception):
            api.get_action('1.1', '1.0', '1.0', 'installed')

    def test_absent_version_doesnt_raise_exception(self):
        api.get_action('absent', '1.0', '1.0', 'installed')

    def test_absent_installed(self):
        self.assertEqual(
            api.get_action('absent', '1.0', '1.0', 'installed'),
            'to remove'
        )

    def test_absent_to_install(self):
        self.assertEqual(
            api.get_action('absent', '1.0', '1.0', 'to install'),
            'to remove'
        )

    def test_absent_to_upgrade(self):
        self.assertEqual(
            api.get_action('absent', '1.0', '1.0', 'to install'),
            'to remove'
        )

    def test_absent_to_remove(self):
        self.assertEqual(
            api.get_action('absent', '1.0', '1.0', 'to remove'),
            False
        )

    def test_absent_uninstalled(self):
        self.assertEqual(
            api.get_action('absent', '1.0', '1.0', 'uninstalled'),
            False
        )

    def test_dont_install_installed(self):
        self.assertEqual(
            api.get_action('1.0', '1.0', '1.0', 'installed'),
            False
        )

    def test_install_uninstalled(self):
        self.assertEqual(
            api.get_action('1.0', '1.0', '1.0', 'uninstalled'),
            'to install'
        )

    def test_upgrade_installed(self):
        self.assertEqual(
            api.get_action('1.1', '1.1', '1.0', 'installed'),
            'to upgrade'
        )

    def test_dont_upgrade_to_upgrade(self):
        self.assertEqual(
            api.get_action('1.1', '1.1', '1.0', 'to upgrade'),
            False
        )


class TestUniformVersion(unittest.TestCase):

    def test_unavailable_version(self):
        self.assertFalse(
            api.get_version('9.0', False),
        )

    def test_absent_module_version_to_complex(self):
        self.assertEquals(
            api.get_version('9.0', 'absent'),
            'absent'
        )
    
    def test_dotless_module_version_to_complex(self):
        self.assertEquals(
            api.get_version('9.0', '1'),
            '9.0.1'
        )

    def test_1_dot_module_version_to_complex(self):
        self.assertEquals(
            api.get_version('9.0', '1.0'),
            '9.0.1.0'
        )

    def test_dont_change_version(self):
        self.assertEquals(
            api.get_version('9.1', '9.0.1'),
            '9.0.1'
        )

        self.assertEquals(
            api.get_version('9.1', '9.0.1.1'),
            '9.0.1.1'
        )
