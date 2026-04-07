from setuptools import find_packages, setup

package_name = 'spi_driver'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'spidev', 'RPi.GPIO', 'shoebot_interfaces'],
    zip_safe=True,
    maintainer='tyler',
    maintainer_email='tylerbartunek@gmail.com',
    description='Handles the SPI transactions with the modules, including module discovery and monitoring',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'spi_hub = spi_driver.bus_hub_node:main',
        ],
    },
)
