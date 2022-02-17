# keyboard_forces
ROS package, Gemini simulator, Input forces through keyboard

Visit Njord challange webisite to setup the enviroment: https://njord.gitbook.io/njord/

Downloaded into catkin_ws/src directory and built with catkin_make. I used VS Code in Ubuntu, where I openend the whole catkin_ws folder which automatically installed missing Cmake.

Reading from the keyboard and Publishing to GeneralizedForce!

Forces act from the center of gravity/origin.

Use 'q' and 'w' for torque control, rotation around the ship's 'z' axes.

Use '8' and '2' for the surge force, along with the ship's heading, and '4' and '6' for the sway force,
perpendicular to the ship's heading.

Each press of the button increases or decreases torque or the force by 20 N or Nm.
Maximum is 100 in each degree of freedom...

Start roscore, ros_client and ros_server first.

Use 'rostopic echo /force_control' in new terminal to observe actual force commanded.

Keep this terminal active. Waiting for the input...
