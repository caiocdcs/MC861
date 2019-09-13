class Stack:
    def __init__(self):
        self.something = 0

    # Getters

    def getSomething(self) -> int:
        return self.something

    # Setters

    def setSomething(self):
        self.something = 1

    # Handlers

    def pushAccumulator(self):
        self.setSomething() # TODO

    def pullAccumulator(self):
        self.setSomething() # TODO

    def pushProcessorStatus(self):
        self.setSomething() # TODO

    def pullProcessorStatus(self):
        self.setSomething() # TODO
       