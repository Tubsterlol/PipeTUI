class EventBus:

    def __init__(self):
        self.listeners = {}

    def subscribe(self, event, func):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(func)

    def publish(self, event, data=None):
        if event in self.listeners:
            for func in self.listeners[event]:
                func(data)
