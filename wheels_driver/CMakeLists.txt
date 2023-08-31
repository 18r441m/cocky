cmake_minimum_required(VERSION 2.8.3)
project(wheels_driver)

find_package(catkin REQUIRED COMPONENTS
  rospy
  cocky_msgs
  tf 
)

catkin_package(
  CATKIN_DEPENDS rospy cocky_msgs tf 
)

catkin_python_setup()

include_directories(
  ${catkin_INCLUDE_DIRS}
)
