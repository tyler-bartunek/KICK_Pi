from setuptools import find_packages, setup

package_name = 'battery_monitor'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'rclpy', 'python3-smbus2', 'python3-ADS1x15-ADC', 'shoebot_interfaces'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='tylerbartunek@gmail.com',
    description='Monitors battery status using the ADS1115 and a voltage divider circuit',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'battery_info_node = battery_monitor.battery_monitor_node:main',
        ],
    },
)
