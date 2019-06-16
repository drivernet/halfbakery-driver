from setuptools import find_packages, setup

setup(
    name='halfbakery_driver',
    version='0.1.2',
    description='Halfbakery communal database controller.',
    url='https://github.com/drivernet/halfbakery-driver',
    author='Mindey',
    author_email='mindey@wefindx.com',
    license='PUBLIC BENEFIT',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires=['metadrive'],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    zip_safe=False
)
