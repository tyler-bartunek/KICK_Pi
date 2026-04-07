FROM ros:jazzy-ros-base
RUN apt-get update && apt-get install -y python3-pip python3-rpi.gpio python3-spidev
RUN pip3 install --break-system-packages smbus2 ADS1x15-ADC