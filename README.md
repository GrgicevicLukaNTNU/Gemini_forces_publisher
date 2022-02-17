# Gemini_forces_publisher
ROS package, Gemini simulator, Input forces through keyboard

Visit Njord challange webisite to setup the enviroment: https://njord.gitbook.io/njord/

Reading from the keyboard and Publishing to GeneralizedForce!

Forces act from the center of gravity. 
Use 'q' and 'w' for torque control, rotation around the ship's 'z' axes.
Use '8' and '2' for the surge force, along with the ship's heading, and '4' and '6' for the sway force,
perpendicular to the ship's heading.
Each press of the button increases or decreases torque or the force by 20 N or Nm.
Maximum is 100 in each degree of freedom...
Use 'rostopic echo /force_control' to observe actual force commanded.
Keep this terminal active. Waiting for the input...
