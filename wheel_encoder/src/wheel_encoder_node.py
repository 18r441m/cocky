#!/usr/bin/env python3
import os.path

import rospy
import uuid
import tf
import yaml

from geometry_msgs.msg import TransformStamped, Transform, Quaternion
from tf2_ros import TransformBroadcaster
from math import pi

from std_msgs.msg import Header
from duckietown_msgs.msg import WheelEncoderStamped, WheelsCmdStamped
from wheel_encoder import WheelEncoderDriver, WheelDirection

class WheelEncoderNode:
    """Node handling a single wheel encoder.

    This node is responsible for reading data off of a single wheel encoders.
    Robots with N wheels will need to spin N instances of this node.
    This node is compatible with any rotary encoder that signals ticks as rising edges
    on a digital GPIO pin.

    For now we use the `wheel_cmd_executed` to determine if we are moving forwards or backwards.
    As a result, if you manually push the robot, you will get potentially incorrect output
    (we default to always forward in this case).

    Subscribers:
       ~wheels_cmd_executed (:obj:`WheemsCmdStamped`): The actual commands executed
    Publishers:
       ~data (:obj:`WheelEncoderStamped`): Publishes the cumulative number of ticks
                                            generated by the encoder.

    """

    def __init__(self, node_name):
        rospy.init_node(node_name)
        # get parameters
        self._veh = rospy.get_param("~veh")
        self._name = rospy.get_param("~name")
        self._gpio_pin = rospy.get_param("~gpio")
        self._resolution = rospy.get_param("~resolution")
        self._configuration = rospy.get_param("~configuration")
        self._publish_frequency = 1

        # try using custom calibration file
        calib_file = os.path.join(
            "/data/config/calibrations/encoder",
            f"{self._configuration}/{self._veh}.yaml",
        )
        try:
            with open(calib_file, "r") as f:
                calib_data = yaml.safe_load(f)
            custom_resolution = int(calib_data["resolution"])
            rospy.set_param("~resolution", custom_resolution)
            self._resolution = custom_resolution
            print(
                (
                    f"With calibration file - {calib_file}, "
                    f"use custom encoder resolution: {self._resolution}"
                )
            )
        except FileNotFoundError:
            print(
                (f"No custom encoder calibration found at: {calib_file}. " "Using default parameters.")
            )
        except KeyError:
            print(
                (
                    "No valid field 'resolution' found in "
                    f"encoder calibration file at: {calib_file}. "
                    "Using default parameters."
                )
            )
        except ValueError:
            print(
                (
                    "No valid integer 'resolution' value found in "
                    f"encoder calibration file at: {calib_file}. "
                    "Using default parameters."
                )
            )
        # throw exceptions for other situations

        # tick storage
        self._tick = 0
        # publisher for wheel encoder ticks
        self._tick_pub = rospy.Publisher(
            "~tick", WheelEncoderStamped, queue_size=1
        )
        # subscriber for the wheel command executed
        self.sub_wheels = rospy.Subscriber(
            "~wheels_cmd_executed", WheelsCmdStamped, self._wheels_cmd_executed_cb, queue_size=1
        )
        # tf broadcaster for wheel frame
        self._tf_broadcaster = TransformBroadcaster()
        # setup a timer
        self._timer = rospy.Timer(rospy.Duration(1.0 / self._publish_frequency), self._cb_publish)
        # setup the driver
        self._driver = WheelEncoderDriver(self._gpio_pin, self._encoder_tick_cb)

    def _wheels_cmd_executed_cb(self, msg):
        if self._configuration == "left":
            if msg.vel_left >= 0:
                self._driver.set_direction(WheelDirection.FORWARD)
            else:
                self._driver.set_direction(WheelDirection.REVERSE)
        elif self._configuration == "right":
            if msg.vel_right >= 0:
                self._driver.set_direction(WheelDirection.FORWARD)
            else:
                self._driver.set_direction(WheelDirection.REVERSE)

    def _encoder_tick_cb(self, tick_no):
        """
        Callback that receives new ticks from the encoder.

            Args:
                tick_no (int): cumulative total number of ticks
        """
        self._tick = tick_no

    def _cb_publish(self, _):
        # Create header with timestamp
        header = Header()
        header.frame_id = f"{self._veh}/{self._name}_wheel_axis"
        header.stamp = rospy.Time.now()
        # publish WheelEncoderStamped message
        self._tick_pub.publish(
            WheelEncoderStamped(
                header=header,
                data=self._tick,
                resolution=self._resolution,
                type=WheelEncoderStamped.ENCODER_TYPE_INCREMENTAL,
            )
        )
        # publish TF
        angle = (float(self._tick) / float(self._resolution)) * 2 * pi
        quat = tf.transformations.quaternion_from_euler(0, angle, 0)
        self._tf_broadcaster.sendTransform(
            TransformStamped(
                header=header,
                child_frame_id=f"{self._veh}/{self._name}_wheel",
                transform=Transform(rotation=Quaternion(x=quat[0], y=quat[1], z=quat[2], w=quat[3])),
            )
        )

if __name__ == "__main__":
    # Initialize the node with rospy
    rand = str(uuid.uuid4())[:8]
    node = WheelEncoderNode("wheel_encoder_%s" % (rand,))
    rospy.on_shutdown(node.on_shutdown)
    # Keep it spinning to keep the node alive
    rospy.spin()
