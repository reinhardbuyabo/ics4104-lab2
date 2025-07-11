import bisect
import hashlib
class ConsistentHashRing:
    def __init__(self, slots=512, virtual_nodes=100):
        self.slots = slots
        self.virtual_nodes = virtual_nodes
        self.ring = {}  # slot -> server_id
        self.sorted_slots = []

    def _hash(self, key: str) -> int:
        h = hashlib.sha256(key.encode()).hexdigest()
        return int(h, 16) % self.slots

    def add_server(self, server_id: int):
        for j in range(self.virtual_nodes):
            key = f"{server_id}-vn{j}"
            slot = self._hash(key)

            # Avoid collision: use linear probing
            original_slot = slot
            while slot in self.ring:
                slot = (slot + 1) % self.slots
                if slot == original_slot:
                    raise Exception("Hash ring is full")

            self.ring[slot] = server_id
            bisect.insort(self.sorted_slots, slot)

    def get_server(self, request_id: int) -> int:
        key = str(request_id)
        request_slot = self._hash(key)
        idx = bisect.bisect_right(self.sorted_slots, request_slot)
        if idx == len(self.sorted_slots):
            idx = 0
        assigned_slot = self.sorted_slots[idx]
        return self.ring[assigned_slot]

    def remove_server(self, server_id: int):
        to_remove = [slot for slot, sid in self.ring.items() if sid == server_id]
        for slot in to_remove:
            del self.ring[slot]
        self.sorted_slots = sorted(self.ring.keys())