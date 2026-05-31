

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='kickbrain',
            executable='test_motor',
            name='motor_send',
            output='screen',
        ),
        Node(
            package='spi_driver',
            executable='spi_hub',
            name='comms_hub',
            output='screen',
        ),
    ])