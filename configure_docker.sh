#!/bin/bash

IMAGE_NAME="shoebot"
CONTAINER_NAME="ShoeBot_container"
WORKSPACE="/home/tyler/Documents/ShoeBot_Pi/sros_ws"

# Check if image exists, build if not
if [ -z "$(docker images -q $IMAGE_NAME)" ]; then
    echo "Image $IMAGE_NAME not found, building..."
    docker build -t $IMAGE_NAME /home/tyler/Documents/ShoeBot_Pi
else
    echo "Image $IMAGE_NAME found, skipping build."
fi

# Check if container already exists and remove it if so
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Removing existing container..."
    docker stop $CONTAINER_NAME 2>/dev/null
    docker rm $CONTAINER_NAME
fi

# Build device flags only for devices that exist
DEVICE_FLAGS=""
for dev in /dev/spidev0.0 /dev/spidev0.1 /dev/gpiomem /dev/gpiochip0; do
    if [ -e "$dev" ]; then
        DEVICE_FLAGS="$DEVICE_FLAGS --device $dev"
    else
        echo "Warning: $dev not found, skipping."
    fi
done

# Run the container
docker run -it --name $CONTAINER_NAME \
    -v $WORKSPACE:/root/colcon_ws \
    $DEVICE_FLAGS \
    $IMAGE_NAME