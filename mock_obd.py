class MockOBD:
    def __init__(self):
        self.speed = 0
        self.rpm = 0

    def set_speed(self, speed):
        self.speed = speed

    def set_rpm(self, rpm):
        self.rpm = rpm

    def query(self, cmd):
        if cmd == obd.commands.SPEED:
            return MockResponse(self.speed)
        elif cmd == obd.commands.RPM:
            return MockResponse(self.rpm)
        return MockResponse(0)

class MockResponse:
    def __init__(self, value):
        self.value = MockValue(value)

class MockValue:
    def __init__(self, magnitude):
        self.magnitude = magnitude

    def to(self, unit):
        # Assume unit conversion is not needed for mock values
        return self