#!/bin/bash

#TODO: Figure out what to do with this to get it to auto-run launching the test nodes within the docker container.

WORKSPACE="/root/colcon_ws"

#Source ros
source /ros_entrypoint.sh

#Check if the kickbot_interfaces, kickbrain, and spi_driver packages are built, if not build them, then launch the test nodes.
if [ ! -d "$WORKSPACE/build/kickbot_interfaces" ] || [ ! -d "$WORKSPACE/build/kickbrain" ] || [ ! -d "$WORKSPACE/build/spi_driver" ]; then
    echo "One or more required packages not built, building now..."
    cd ../
    colcon build --packages-select kickbot_interfaces kickbrain spi_driver --executor sequential
else
    echo "All required packages already built, skipping build."
fi

#Source the local workspace
source "$WORKSPACE/install/local_setup.sh"

cd $WORKSPACE/launch

ros2 launch launch_kick_echo_test.py