from setuptools import setup, find_packages

setup(
    name='pygments-pprint-sql',
    version='0.1.0',
    description='Pretty format your SQL queries for easier reading.',
    author='Nathan Wright',
    author_email='thatnateguy@gmail.com',
    url='http://github.com/natedub/pygments-pprint-sql',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
    ],

    install_requires=[
        'Pygments',
    ],

    packages=find_packages(exclude=['ez_setup']),

    entry_points="""
    [pygments.filters]
    pprint-sql = pygments_pprint_sql:SqlFilter
    """,
)
