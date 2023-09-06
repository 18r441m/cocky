#!/usr/bin/env python3

import rospy
import RPi.GPIO as GPIO
from duckietown_msgs.msg import WheelsCmdStamped, WheelTicks

FORWARD = 1
REVERSE = -1

class EncoderNode:

    def __init__(self):
        rospy.init_node('encoder_node', anonymous=True)
        rospy.on_shutdown(self.on_shutdown)

        self.left_ticks = 0
        self.right_ticks = 0
        self.left_direction = FORWARD
        self.right_direction = FORWARD

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(18, GPIO.IN)
        GPIO.setup(19, GPIO.IN)

        GPIO.add_event_detect(18, GPIO.RISING, callback=self.left_encoder_cb)
        GPIO.add_event_detect(19, GPIO.RISING, callback=self.right_encoder_cb)

        self.left_pub = rospy.Publisher('~left_wheel_ticks', WheelTicks, queue_size=10)
        self.right_pub = rospy.Publisher('~right_wheel_ticks', WheelTicks, queue_size=10)
        
        rospy.Subscriber('~wheels_cmd_executed', WheelsCmdStamped, self._wheels_cmd_executed_cb)  # replace with actual topic and msg type

        rate = rospy.Rate(10)  # 10 Hz

        while not rospy.is_shutdown():
            left_msg = WheelTicks()
            left_msg.wheel_name = 'left'
            left_msg.ticks = self.left_ticks

            right_msg = WheelTicks()
            right_msg.wheel_name = 'right'
            right_msg.ticks = self.right_ticks

            self.left_pub.publish(left_msg)
            self.right_pub.publish(right_msg)

            rate.sleep()

    def left_encoder_cb(self, channel):
        self.left_ticks += self.left_direction

    def right_encoder_cb(self, channel):
        self.right_ticks += self.right_direction

    def _wheels_cmd_executed_cb(self, msg):
        if msg.vel_left >= 0:
            self.left_direction = FORWARD
        else:
            self.left_direction = REVERSE

        if msg.vel_right >= 0:
            self.right_direction = FORWARD
        else:
            self.right_direction = REVERSE

    def on_shutdown(self):
        rospy.loginfo("Shutting down EncoderNode...")
        GPIO.remove_event_detect(18)
        GPIO.remove_event_detect(19)
        GPIO.cleanup()

if __name__ == '__main__':
    try:
        EncoderNode()
    except rospy.ROSInterruptException:
        pass  # the on_shutdown function will handle the GPIO cleanup
