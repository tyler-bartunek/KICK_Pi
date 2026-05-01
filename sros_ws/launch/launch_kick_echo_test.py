
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='kickbrain',
            executable='test_echo',
            name='echo_send',
            output='screen',
        ),
        Node(
            package='spi_driver',
            executable='echo_hub',
            name='echo_return',
            output='screen',
        ),
    ])