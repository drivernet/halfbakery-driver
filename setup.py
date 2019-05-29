from setuptools import find_packages, setup

setup(
    name='halfbakery',
    version='0.0.5',
    description='Halfbakery communal database controller.',
    url='https://gitlab.com/drivernet/halfbakery',
    author='Mindey',
    author_email='mindey@wefindx.com',
    license='ASK FOR PERMISSIONS',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires=['metadrive'],
    extras_require = {
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    zip_safe=False
)
