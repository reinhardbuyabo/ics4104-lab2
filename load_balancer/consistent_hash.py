import bisect
import hashlib

M = 512  # total slots
K = 9    # virtual servers per physical server


class ConsistentHashRing:
    def __init__(self):
        self.ring = dict()  # slot_index -> server_id
        self.sorted_slots = []

    def _hash_request(self, i: int) -> int:
        return (i ** 2 + 2 * i + 17) % M

    def _hash_virtual_server(self, i: int, j: int) -> int:
        return (i ** 2 + j + 2 * j + 25) % M

    def add_server(self, server_id: int):
        for j in range(K):
            slot = self._hash_virtual_server(server_id, j)
            original_slot = slot

            # Handle collisions with linear probing
            while slot in self.ring:
                slot = (slot + 1) % M
                if slot == original_slot:
                    raise Exception("Hash ring is full")

            self.ring[slot] = server_id
            bisect.insort(self.sorted_slots, slot)

    def get_server(self, request_id: int) -> int:
        request_slot = self._hash_request(request_id)
        idx = bisect.bisect_right(self.sorted_slots, request_slot)

        # wrap around if needed
        if idx == len(self.sorted_slots):
            idx = 0

        assigned_slot = self.sorted_slots[idx]
        return self.ring[assigned_slot]
