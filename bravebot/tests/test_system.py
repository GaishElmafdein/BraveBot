import unittest
from src.check_system import check_system_status

class TestSystem(unittest.TestCase):
    
    def test_check_system_status(self):
        status = check_system_status()
        self.assertIn('AI Engine', status)
        self.assertIn('Telegram Bot', status)
        self.assertIn('Dashboard', status)
        
        self.assertTrue(status['AI Engine']['active'])
        self.assertTrue(status['Telegram Bot']['active'])
        self.assertTrue(status['Dashboard']['active'])

if __name__ == '__main__':
    unittest.main()