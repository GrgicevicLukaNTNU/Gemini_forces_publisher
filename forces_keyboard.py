#!/usr/bin/env python

from __future__ import print_function
import tty
import termios
import select
import sys
from ros_clients.msg import GeneralizedForce
import rospy

import threading

import roslib
roslib.load_manifest('keyboard_forces')


msg = """
Reading from the keyboard and Publishing to GeneralizedForce!

Forces act from the center of gravity. 
Use 'q' and 'w' for torque control, rotation around the ship's 'z' axes.
Use '8' and '2' for the surge force, along with the ship's heading, and '4' and '6' for the sway force,
perpendicular to the ship's heading.
Each press of the button increases or decreases torque or the force by 20 N or Nm.
Maximum is 100 in each degree of freedom...
Use 'rostopic echo /force_control' to observe actual force commanded.
Keep this terminal active. Waiting for the input...
"""

Bindings = {
    '8': (20, 0, 0, 0, 0, 0),  # x plus
    '2': (0, -20, 0, 0, 0, 0),  # x minus
    '4': (0, 0, -20, 0, 0, 0),  # y minus
    '6': (0, 0, 0, 20, 0, 0),  # y plus
    'q': (0, 0, 0, 0, -20, 0),  # n minus
    'w': (0, 0, 0, 0, 0, 20),  # n plus
}


class PublishThread(threading.Thread):
    def __init__(self, rate):
        super(PublishThread, self).__init__()
        self.publisher = rospy.Publisher(
            'force_control', GeneralizedForce, queue_size=1)
        self.x_p = 0.0
        self.y_p = 0.0
        self.n_p = 0.0
        self.x_m = 0.0
        self.y_m = 0.0
        self.n_m = 0.0
        self.condition = threading.Condition()
        self.done = False

        # Set timeout to None if rate is 0 (causes new_message to wait forever
        # for new data to publish)
        if rate != 0.0:
            self.timeout = 1.0 / rate
        else:
            self.timeout = None

        self.start()

    def wait_for_subscribers(self):
        i = 0

        while not rospy.is_shutdown() and self.publisher.get_num_connections() == 0:

            print("Waiting for subscriber to connect to {}".format(
                self.publisher.name))

            break

        if rospy.is_shutdown():
            raise Exception(
                "Got rospy shutdown request before subscribers connected")

    def update(self, x_p, y_p, n_p, x_m, y_m, n_m):
        self.condition.acquire()
        self.x_p = self.x_p + x_p
        self.y_p = self.y_p + y_p
        self.n_p = self.n_p + n_p
        self.x_m = self.x_m + x_m
        self.y_m = self.y_m + y_m
        self.n_m = self.n_m + n_m
        # Notify publish thread that we have a new message.
        self.condition.notify()
        self.condition.release()

    def stop(self):
        self.done = True
        self.update(0, 0, 0, 0, 0, 0)
        self.join()

    def run(self):
        force = GeneralizedForce()

        while not self.done:
            self.condition.acquire()
            # Wait for a new message or timeout.
            self.condition.wait(self.timeout)

            # Check for maximumm force/torque
            sum_x = self.x_p + self.x_m
            sum_y = self.y_p + self.y_m
            sum_n = self.n_p + self.n_m

            if sum_x > 100:
                sum_x = 100

            if sum_x < -100:
                sum_x = -100

            if sum_y > 100:
                sum_y = 100

            if sum_y < -100:
                sum_y = -100

            if sum_n > 100:
                sum_n = 100

            if sum_n < -100:
                sum_n = -100

            # Copy state into force message.
            force.x = sum_x
            force.y = sum_y
            force.z = 0
            force.k = 0
            force.m = 0
            force.n = sum_n

            self.condition.release()

            # Publish.
            self.publisher.publish(force)

        # Publish stop message when thread exits.
        force.x = 0
        force.y = 0
        force.z = 0
        force.k = 0
        force.m = 0
        force.n = 0
        self.publisher.publish(force)


def getKey(key_timeout):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], key_timeout)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

    return key


if __name__ == "__main__":

    settings = termios.tcgetattr(sys.stdin)

    rospy.init_node('keyboard_forces')

    repeat = rospy.get_param("~repeat_rate", 0.0)
    key_timeout = rospy.get_param("~key_timeout", 0.0)

    if key_timeout == 0.0:
        key_timeout = None

    pub_thread = PublishThread(repeat)

    x_p = 0
    y_p = 0
    n_p = 0
    x_m = 0
    y_m = 0
    n_m = 0

    try:

        pub_thread.wait_for_subscribers()

        pub_thread.update(x_p, y_p, n_p, x_m, y_m, n_m)

        print(msg)

        while(1):

            key = getKey(key_timeout)

            if key in Bindings.keys():

                x_p = Bindings[key][0]
                y_p = Bindings[key][3]
                n_p = Bindings[key][5]
                x_m = Bindings[key][1]
                y_m = Bindings[key][2]
                n_m = Bindings[key][4]

            else:

                if (key == '\x03'):
                    break

            pub_thread.update(x_p, y_p, n_p, x_m, y_m, n_m)

    except Exception as e:
        print(e)

    finally:
        pub_thread.stop()

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
