# Stack memory: $0100–$01FF

class Stack:
    def __init__(self):
        self.address = 256 + 255 # stack starts at 0x01ff

    # Getters

    def getAddress(self) -> int:
        return self.address
