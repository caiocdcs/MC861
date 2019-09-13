# Stack memory: $0100–$01FF

class Stack:
    def __init__(self):
        self.address = 256

    # Getters

    def getAddress(self) -> int:
        return self.address
