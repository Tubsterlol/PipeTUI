import psutil
import time


class MonitorService:

    def __init__(self, event_bus, config):
        self.event_bus = event_bus
        self.config = config

    def start_monitoring(self):

        while True:

            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent

            print(f"CPU: {cpu}% | Memory: {memory}%")

            if cpu > self.config.cpu_threshold:
                self.event_bus.publish("cpu_high", cpu)

            if memory > self.config.memory_threshold:
                self.event_bus.publish("memory_high", memory)

            time.sleep(5)