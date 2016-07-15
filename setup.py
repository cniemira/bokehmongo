from setuptools import setup, find_packages

setup(name='bokehmongo',
      author='CJ Niemira',
      author_email='siege@siege.org',
      version='0.1',
      description='This is a horrible thing',
      classifiers=[
          "Programming Language :: Python",
      ],
      url='https://github.com/cniemira/bokehmongo',
      packages=find_packages(),
      install_requires=['bokeh', 'numpy', 'ipywidgets']
      )
