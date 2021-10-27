from setuptools import setup, find_packages

setup(
    name="minipoker",
    version="0.0.1",
    author="arslan",
    author_email="oyyoson@gmail.com",
    description="迷你德州内测",
    url="https://github.com/nosoyyo/minipoker", 
    packages=find_packages(),

    classifiers = [
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.5',
    ],

    package_data={
        '':['*.py'],
        'bandwidth_reporter':['*.py']
               },
    exclude_package_data={
        'bandwidth_reporter':['*.md'],
    },
    install_requires=['rich','pynput','thpoker','transitions'],
    tests_require=[
        'pytest>=3.3.1',
        'pytest-cov>=2.5.1',
    ],

)