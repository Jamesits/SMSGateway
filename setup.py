from setuptools import setup

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
    author_email='github@public.swineson.me',
    url="https://swineson.me/",
    packages=['SMSGateway'],  # same as name
    install_requires=['aiosmtpd', 'pytz', 'smpplib', 'pystache', 'python-telegram-bot', 'toml', 'gsm0338'],
    entry_points={
        'console_scripts': [
            'smsgateway=SMSGateway.__main__:main'
        ]
    }
)
