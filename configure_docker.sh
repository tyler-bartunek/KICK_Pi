#!/bin/bash

# Check if all required devices exist before allowing a build/run
DEVICES_OK=true
for dev in /dev/spidev0.0 /dev/spidev0.1 /dev/gpiomem /dev/gpiochip0; do
    if [ ! -e "$dev" ]; then
        echo "Warning: $dev not found."
        DEVICES_OK=false
    fi
done

if [ "$DEVICES_OK" = true ]; then
    docker compose up --build
else
    echo "Required devices missing, skipping build/run."
    exit 1
fi