from setuptools import setup

setup(
    name='30x-it',
    version='0.1.0',
    url='https://github.com/underyx/30x-it',
    author='Bence Nagy',
    author_email='bence@underyx.me',
    download_url='https://github.com/underyx/30x-it/releases',
    packages=['starpicker'],
    install_requires=[
        'aiohttp<3.8',
        'aioredis<0.3',
        'cchardet<3',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ]
)
