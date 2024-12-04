import obd
import threading
import time

class MockOBD:
    def __init__(self):
        self.speed = 0
        self.rpm = 0
        self.target_speed = 0
        self.target_rpm = 0
        self.update_interval = 0.03  # Shorter intervals for smoother updates
        self.smoothing_factor = 0.1  # Controls the rate of change (0.1 = 10% of the difference)

        # Start background thread for gradual updates
        self.running = True
        self.update_thread = threading.Thread(target=self._update_values)
        self.update_thread.daemon = True
        self.update_thread.start()

    def set_speed(self, target_speed):
        """Set the target speed for gradual adjustment."""
        self.target_speed = target_speed

    def set_rpm(self, target_rpm):
        """Set the target RPM for gradual adjustment."""
        self.target_rpm = target_rpm

    def _update_values(self):
        """Gradually update speed and RPM toward target values."""
        while self.running:
            # Smoothly approach the target speed
            if self.speed != self.target_speed:
                diff = self.target_speed - self.speed
                self.speed += diff * self.smoothing_factor

            # Smoothly approach the target RPM
            if self.rpm != self.target_rpm:
                diff = self.target_rpm - self.rpm
                self.rpm += diff * self.smoothing_factor

            # Sleep for the defined interval before the next update
            time.sleep(self.update_interval)

    def query(self, cmd):
        """Return the current value for the requested command."""
        if cmd == obd.commands.SPEED:
            return MockResponse(self.speed)
        elif cmd == obd.commands.RPM:
            return MockResponse(self.rpm)
        return MockResponse(0)

    def stop(self):
        """Stop the background thread."""
        self.running = False
        self.update_thread.join()

class MockResponse:
    def __init__(self, value):
        self.value = MockValue(value)

class MockValue:
    def __init__(self, magnitude):
        self.magnitude = magnitude

    def to(self, unit):
        return self


# OBDHandler Implementation
class OBDHandler:
    def __init__(self, connection=None):
        self.connection = connection or MockOBD()  # Default to MockOBD for testing
        self.speed = 0
        self.rpm = 0
    
    def get_speed(self):
        cmd = obd.commands.SPEED  # Select OBD speed command
        response = self.connection.query(cmd)
        return response.value.to("mph").magnitude

    def get_rpm(self):
        cmd = obd.commands.RPM  # Select OBD RPM command
        response = self.connection.query(cmd)
        return response.value.magnitude

    def refresh(self):
        """Updates speed and RPM values."""
        self.rpm = self.get_rpm()
        self.speed = self.get_speed()

    def get_bass_volume(self):
        bass_percent = self.rpm / 7000
        bass_volume = min(bass_percent + 0.5, 1)
        return bass_volume

    def get_drums_volume(self):
        drums_percent = self.speed / 70
        drums_volume = max(min(drums_percent * 7 - 1, 1), 0)
        return drums_volume

    def get_other_volume(self):
        other_percent = self.speed / 70
        other_volume = max(min(other_percent * 7 - 2.5, 1), 0)
        return other_volume

    def get_vocals_volume(self):
        vocals_percent = self.speed / 70
        vocals_volume = max(min(vocals_percent * 7 - 4, 1), 0)
        return vocals_volume

    def get_volumes(self):
        """Returns a list of calculated volumes."""
        return [
            self.get_bass_volume(),
            self.get_drums_volume(),
            self.get_other_volume(),
            self.get_vocals_volume(),
        ]
