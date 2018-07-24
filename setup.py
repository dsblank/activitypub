import io
import sys
try:
    import pypandoc
except:
    pypandoc = None

from setuptools import find_packages, setup

with io.open('activitypub/_version.py', encoding='utf-8') as fid:
    for line in fid:
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break

with io.open('README.md', encoding='utf-8') as fp:
    long_desc = fp.read()
    if pypandoc is not None:
        try:
            long_desc = pypandoc.convert(long_desc, "rst", "markdown_github")
        except:
            pass


setup(name='activitypub',
      version=version,
      description='A general Python ActivityPub library',
      long_description=long_desc,
      author='Douglas S. Blank',
      author_email='doug.blank@gmail.com',
      url='https://github.com/dsblank/activitypub',
      install_requires=[],
      packages=find_packages(include=['activitypub', 'activitypub.*']),
      include_data_files = True,
      test_suite = 'nose.collector',
      classifiers=[
          'Framework :: IPython',
          'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
          'Programming Language :: Python :: 3',
      ]
)
