# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='python-joris2k-ble',
    version='0.1.0',
    packages=['joris2k_ble'],
    python_requires='>=3.5',
    install_requires=['bluepy>=1.0.5', 'click', 'construct', 'click-datetime'],
    description='Joris2k bluetooth low energy (BLE) devices library',
    author='Joris Dobbelsteen',
    author_email='joris@familiedobbelsteen.nl',
    maintainer='Joris Dobbelsteen',
    maintainer_email='joris@familiedobbelsteen.nl',
    # url='https://github.com/rytilahti/python-eq3bt.git',
    license="MIT",
    entry_points={
        'console_scripts': [
            'joris2kblecli = joris2k_ble.joris2kblecli:cli'
        ]
    }
)
