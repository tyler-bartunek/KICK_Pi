FROM ros:jazzy-ros-base
RUN apt-get update && apt-get install -y python3-pip python3-spidev python3-numpy
RUN pip3 install --break-system-packages smbus2 ADS1x15-ADC gpiod