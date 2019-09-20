from ctypes import c_uint8
from copy import copy

class Memory:
    def __init__(self):
        self.memory = [c_uint8(0)]*1024*64    # 64 KB

    def get_memory_at_position_str(self, pos) -> c_uint8:
        return copy(self.memory[int(pos, 16)])
    
    def set_memory_at_position_str(self, pos, data):
        self.memory[int(pos, 16)] = copy(data)

    def get_memory_at_position_int(self, pos) -> c_uint8:
        return copy(self.memory[pos])
    
    def set_memory_at_position_int(self, pos, data):
        self.memory[pos] = copy(data)
        