from setuptools import find_packages, setup

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='django-controlcenter',
    version='0.3.1',
    description='Set of widgets to build dashboards for your Django-project.',
    long_description=long_description,
    url='https://github.com/byashimov/django-controlcenter',
    author='Murad Byashimov',
    author_email='byashimov@gmail.com',
    packages=find_packages(
        exclude=['controlcenter.stylus', 'controlcenter.images']),
    include_package_data=True,
    license='BSD',
    install_requires=['django-pkgconf~=0.4.0'],
    keywords='django admin dashboard',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Framework :: Django',
        'Framework :: Django :: 1',
        'Framework :: Django :: 2',
        'Framework :: Django :: 3',
        'Framework :: Django :: 4',
    ],
)
