from setuptools import find_packages, setup

package_name = 'kickbrain'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tyler',
    maintainer_email='tylerbartunek@gmail.com',
    description='Main node for monitoring Kick Robot state and behavior',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'kickbrain = kickbrain.kickbrain_node:main',
            'test_echo = kickbrain.test_echo_node:main',
        ],
    },
)
