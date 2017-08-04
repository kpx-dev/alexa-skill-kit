"""
Alexa Skill Kit for Python
--------------------------

Help you create Alexa skill super easy in Python, like 20 lines of code, promise!

Please go to the repo for more info on getting started: https://github.com/KNNCreative/alexa-skill-kit
"""
from setuptools import setup, find_packages
from alexa_skill_kit import __version__

setup(
    name='alexa-skill-kit',
    version=__version__,
    url='https://github.com/KNNCreative/alexa-skill-kit',
    license='MIT',
    author='Kien Pham',
    author_email='kien@knncreative.com',
    description='Alexa Skill Kit for Python',
    long_description=__doc__,
    packages=['alexa_skill_kit'],
    zip_safe=True,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'boto3',
        'requests',
    ],
    test_suite='tests',
    keywords = ['alexa skill kit', 'alexa', 'skill kit', 'alex echo', 'alexa ask', 'aws alexa'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
