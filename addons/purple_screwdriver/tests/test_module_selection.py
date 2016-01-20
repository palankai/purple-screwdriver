import unittest

from .. import api


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
