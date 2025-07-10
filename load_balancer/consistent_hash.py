import bisect

import math

class ConsistentHashRing:
    def __init__(self, num_slots=512, num_replicas=None):
        self.num_slots = num_slots
        self.num_replicas = num_replicas or int(math.log2(num_slots))
        self.ring = {}               # slot -> server_id
        self.sorted_slots = []       # sorted list of slot numbers
        self.server_ids = set()      # physical server ids

    # Hash function for request ID
    def request_hash(self, rid):
        return (rid + pow(2, rid, self.num_slots) + 17) % self.num_slots

    # Hash function for virtual server ID
    def virtual_server_hash(self, sid: str, replica_index: int):
        sid_num = sum(ord(c) for c in sid)  # convert server id string to numeric
        return (sid_num + replica_index + pow(2, replica_index, self.num_slots) + 25) % self.num_slots

    # Add a physical server and its virtual nodes
    def add_server(self, server_id: str):
        if server_id in self.server_ids:
            return
        self.server_ids.add(server_id)
        for j in range(self.num_replicas):
            slot = self.virtual_server_hash(server_id, j)
            original_slot = slot
            # Handle collision via linear probing
            while slot in self.ring:
                slot = (slot + 1) % self.num_slots
                if slot == original_slot:
                    raise Exception("Hash ring is full!")
            self.ring[slot] = server_id
            bisect.insort(self.sorted_slots, slot)

    # Remove a server and its virtual nodes
    def remove_server(self, server_id: str):
        self.server_ids.discard(server_id)
        slots_to_remove = [slot for slot, sid in self.ring.items() if sid == server_id]
        for slot in slots_to_remove:
            del self.ring[slot]
            self.sorted_slots.remove(slot)

    # Get the server that should handle the given request ID
    def get_server(self, request_id: int):
        slot = self.request_hash(request_id)
        idx = bisect.bisect_right(self.sorted_slots, slot)
        if idx == len(self.sorted_slots):  # wrap around
            idx = 0
        target_slot = self.sorted_slots[idx]
        return self.ring[target_slot]

        assigned_slot = self.sorted_slots[idx]
        return self.ring[assigned_slot]
    
    def remove_server(self, server_id: int):
        to_remove = [slot for slot, sid in self.ring.items() if sid == server_id]
        for slot in to_remove:
            del self.ring[slot]
        self.sorted_slots = sorted(self.ring.keys())

    # Optional: return current mapping (useful for debugging or /rep endpoint)
    def get_ring_snapshot(self):
        return {slot: self.ring[slot] for slot in self.sorted_slots}