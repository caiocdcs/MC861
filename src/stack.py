# Stack memory: $0100–$01FF

class Stack:
    def __init__(self):
        self.address = 0x0100 # stack starts at 0x0100

    # Getters

    def getAddress(self) -> int:
        return self.address
