from ctypes import c_uint8

class Memory:
    def __init__(self):
        self.memory = [0]*1024*64    # 64 KB

    def get_memory_at_position(self, pos) -> c_uint8:
        return self.memory[int(pos, 16)]
    
    def set_memory_at_position(self, pos, data):
        self.memory[int(pos, 16)] = data