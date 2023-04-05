"""See README.md for package documentation."""

from setuptools import setup, find_namespace_packages

from io import open
from os import path

here = path.abspath(path.dirname(__file__))

filename = path.join(here, 'kivy_garden', 'navigationdrawer', '_version.py')
locals = {}
with open(filename, "rb") as fh:
    exec(compile(fh.read(), filename, 'exec'), globals(), locals)
__version__ = locals['__version__']

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

URL = 'https://github.com/Tungsteno74/navigationdrawer'

setup(
    name='kivy_garden.navigationdrawer',
    version=__version__,
    description='Android Side Panel like widget.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=URL,
    author='Kivy',
    author_email='kivy@kivy.org',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='Kivy kivy-garden',

    packages=find_namespace_packages(include=['kivy_garden.*']),
    install_requires=[],
    extras_require={
        'dev': ['pytest>=3.6', 'pytest-cov', 'pytest-asyncio',
                'sphinx_rtd_theme'],
        'ci': ['coveralls', 'pycodestyle'],
    },
    package_data={'':['navigationdrawer_gradient_ltor.png', 'navigationdrawer_gradient_rtol.png']},
    data_files=[],
    entry_points={},
    project_urls={
        'Bug Reports': URL + '/issues',
        'Source': URL,
    },
)
