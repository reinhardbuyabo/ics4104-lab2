import unittest
from consistent_hash import ConsistentHashRing


class TestConsistentHashRing(unittest.TestCase):
    def setUp(self):
        self.ring = ConsistentHashRing()
        self.ring.add_server(1)
        self.ring.add_server(2)
        self.ring.add_server(3)

    def test_virtual_nodes_added(self):
        # Should be 3 servers * 9 virtual nodes
        self.assertEqual(len(self.ring.ring), 27)

    def test_ring_sorted(self):
        self.assertEqual(sorted(self.ring.sorted_slots), self.ring.sorted_slots)

    def test_request_mapping(self):
        server = self.ring.get_server(123456)
        self.assertIn(server, [1, 2, 3])

    def test_no_overlap_slots(self):
        # Ensure no duplicate slots were inserted
        self.assertEqual(len(self.ring.sorted_slots), len(set(self.ring.sorted_slots)))


if __name__ == '__main__':
    unittest.main()
