#!/bin/bash

set -e

# Update and Upgrade
echo "Updating package list..."
sudo apt update
echo "Upgrading installed packages..."
sudo apt upgrade -y

# Install tools
echo "Installing curl, vim, and tmux..."
sudo apt install curl vim tmux

# Install python pip
echo "Installing python3-pip..."
sudo apt install python3-pip

# Setup ROS repositories
echo "Setting up ROS repositories..."
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
echo "Adding ROS keys..."
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
echo "Updating package list with ROS repos..."
sudo apt update

# Install ROS Noetic Desktop Full
echo "Installing ROS Noetic Desktop Full..."
sudo apt install ros-noetic-desktop-full

# Source ROS setup.bash in bashrc
echo "Sourcing ROS setup in bashrc..."
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc

# Copy udev rules
echo "Copying udev rules..."
sudo cp 99-duckiebot.rules /etc/udev/rules.d/

# Rebooting
echo "Rebooting now..."
sudo reboot
