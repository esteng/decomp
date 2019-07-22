from setuptools import setup

setup(name='Decomp',
      version='1.0',
      description='Toolkit for working with Universal\
                   Decompositional Semantics graphs',
      url='https://decomp.io/',
      author='Aaron Steven White',
      author_email='aaron.white@rochester.edu',
      license='MIT',
      packages=['decomp'],
      package_dir={'decomp': 'decomp'},
      package_data={'decomp': ['data/*']},
      install_requires=['json==2.0.9',
                        'pyparsing==2.4.0',
                        'requests==2.22.0',
                        'networkx==2.2',
                        'rdflib==4.2.2',
                        'predpatt',
                        'memoized-property'],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
