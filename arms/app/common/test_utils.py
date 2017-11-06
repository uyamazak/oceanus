import unittest
from common.utils import get_client_rad


class TestGetClientRad(unittest.TestCase):

    def test_get_client_rad1(self):
        pat1 = ['unknown', '111.111.111.111', '222.222.222.222', '130.211.0.0']
        self.assertEqual(get_client_rad(pat1), '222.222.222.222')

    def test_get_client_rad2(self):
        pat2 = ['111.111.111.111', '222.222.222.222', '130.211.0.0']
        self.assertEqual(get_client_rad(pat2), '222.222.222.222')

    def test_get_client_rad3(self):
        pat3 = ['222.222.222.222', '130.211.0.0']
        self.assertEqual(get_client_rad(pat3), '222.222.222.222')

    def test_get_client_rad4(self):
        pat4 = ['222.222.222.222']
        self.assertEqual(get_client_rad(pat4), '222.222.222.222')


if __name__ == '__main__':
    unittest.main()
