import unittest
from hamstertracsyncr import activity_contains_ticket

class TestActivityContainsTicket(unittest.TestCase):
    
    def test_returns_valid_ticket(self):
        self.assertEquals(activity_contains_ticket('#475'), 475)
    
    def test_returns_false_on_no_ticket(self):
        self.assertEquals(activity_contains_ticket('Something with a # in it.'), False)
        
    def test_returns_on_ticket_not_at_start(self):
        self.assertEquals(activity_contains_ticket('Something with a #475 in it.'), 475)
        
    def test_returns_on_ticket_with_category(self):
        self.assertEquals(activity_contains_ticket('#475@MyCategory.'), 475)
    