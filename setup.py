from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='SMSGateway',
    version='0.0.1',
    description='SMS routing toolkit for VOIP devices',
    license="Proprietary",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='James Swineson',
    author_email='pypi@public.swineson.me',
    url="https://github.com/Jamesits/SMSGateway",
    packages=find_packages(),
    install_requires=['aiosmtpd', 'pytz', 'smpplib', 'pystache', 'python-telegram-bot', 'toml', 'gsm0338'],
    entry_points={
        'console_scripts': [
            'smsgateway=SMSGateway.__main__:main'
        ]
    }
)
