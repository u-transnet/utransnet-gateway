from distutils.core import setup

requirements = [
    'django==2.0.2',
    'bitshares==0.1.11',
    'graphenelib==0.5.9',
    'gunicorn',
    'git+https://github.com/u-transnet/python-utransnet@transnet_naming',
    'django-jet',
    'django-two-factor-auth',
    'twilio'
]

if __name__ == '__setup__':
    setup(
        name='utransnet-gateway',
        version='1.0',
        url='https://github.com/u-transnet/utransnet-gateway',
        license='MIT',
        author='Ilya Shmelev',
        author_email='ishmelev23@gmail.com',
        description='Gateway',
        requires=requirements
    )
