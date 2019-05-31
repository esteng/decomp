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
      install_requires=['numpy',
                        'scipy',
                        'pandas',
                        'networkx',
                        'predpatt'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
