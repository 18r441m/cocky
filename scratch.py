 import RPi.GPIO as GPIO
import time

class DuckiebotDriver:
    FORWARD = 1
    REVERSE = -1
    LEFT_WHEEL_PIN = 18
    RIGHT_WHEEL_PIN = 19
    

    def __init__(self):
        self.left_ticks = 0
        self.right_ticks = 0
        self.left_direction = self.FORWARD
        self.right_direction = self.FORWARD

        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LEFT_WHEEL_PIN, GPIO.IN)
        GPIO.setup(self.RIGHT_WHEEL_PIN, GPIO.IN)


        GPIO.add_event_detect(self.LEFT_WHEEL_PIN, GPIO.RISING, callback=self._left_encoder_cb)
        GPIO.add_event_detect(self.RIGHT_WHEEL_PIN, GPIO.RISING, callback=self._right_encoder_cb)

    def _left_encoder_cb(self, channel):
        self.left_ticks += self.left_direction
        print(f"Left Ticks: {self.left_ticks}")

    def _right_encoder_cb(self, channel):
        self.right_ticks += self.right_direction
        print(f"Right Ticks: {self.right_ticks}")

    def shutdown(self):
        self.left_pwm.stop()
        self.right_pwm.stop()
        GPIO.remove_event_detect(self.LEFT_WHEEL_PIN)
        GPIO.remove_event_detect(self.RIGHT_WHEEL_PIN)
        GPIO.cleanup()

if __name__ == "__main__":
    driver = DuckiebotDriver()
