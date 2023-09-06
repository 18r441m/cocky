 import RPi.GPIO as GPIO
import time

class DuckiebotDriver:
    FORWARD = 1
    REVERSE = -1
    LEFT_WHEEL_PIN = 18
    RIGHT_WHEEL_PIN = 19
    LEFT_PWM_PIN = 20  # Set this to the actual GPIO pin connected to the left motor driver
    RIGHT_PWM_PIN = 21  # Set this to the actual GPIO pin connected to the right motor driver

    def __init__(self):
        self.left_ticks = 0
        self.right_ticks = 0
        self.left_direction = self.FORWARD
        self.right_direction = self.FORWARD

        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.LEFT_WHEEL_PIN, GPIO.IN)
        GPIO.setup(self.RIGHT_WHEEL_PIN, GPIO.IN)
        GPIO.setup(self.LEFT_PWM_PIN, GPIO.OUT)
        GPIO.setup(self.RIGHT_PWM_PIN, GPIO.OUT)

        self.left_pwm = GPIO.PWM(self.LEFT_PWM_PIN, 1000)  # Initialize PWM on LEFT_PWM_PIN with 1kHz frequency
        self.right_pwm = GPIO.PWM(self.RIGHT_PWM_PIN, 1000)

        GPIO.add_event_detect(self.LEFT_WHEEL_PIN, GPIO.RISING, callback=self._left_encoder_cb)
        GPIO.add_event_detect(self.RIGHT_WHEEL_PIN, GPIO.RISING, callback=self._right_encoder_cb)

    def _left_encoder_cb(self, channel):
        self.left_ticks += self.left_direction
        print(f"Left Ticks: {self.left_ticks}")

    def _right_encoder_cb(self, channel):
        self.right_ticks += self.right_direction
        print(f"Right Ticks: {self.right_ticks}")

    def set_wheel_speed(self, left_speed, right_speed):
        # Speed should be a float between -1.0 and 1.0
        if left_speed >= 0:
            self.left_direction = self.FORWARD
        else:
            self.left_direction = self.REVERSE
        if right_speed >= 0:
            self.right_direction = self.FORWARD
        else:
            self.right_direction = self.REVERSE

        left_duty_cycle = abs(left_speed) * 100  # Converting speed to duty cycle
        right_duty_cycle = abs(right_speed) * 100

        self.left_pwm.start(left_duty_cycle)
        self.right_pwm.start(right_duty_cycle)

    def shutdown(self):
        self.left_pwm.stop()
        self.right_pwm.stop()
        GPIO.remove_event_detect(self.LEFT_WHEEL_PIN)
        GPIO.remove_event_detect(self.RIGHT_WHEEL_PIN)
        GPIO.cleanup()

    def test_drive(self):
        try:
            while True:
                self.set_wheel_speed(0.5, 0.5)
                time.sleep(1)
                self.set_wheel_speed(-0.5, -0.5)
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

if __name__ == "__main__":
    driver = DuckiebotDriver()
    driver.test_drive()
