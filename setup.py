import setuptools

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

with open('dev/version.py') as fd:
    version = fd.read().split('=')[1].replace("'", '').strip()

with open('requirements/base.txt') as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="dev",
    version=version,
    author="MasonData",
    author_email="engineering@mason.app",
    description="The Development Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MasonData/dev",
    project_urls={
        "Bug Tracker": "https://github.com/MasonData/dev/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    packages=setuptools.find_packages(include=['dev*']),
    namespace_packages=['dev'],
    install_requires=install_requires,
    package_data={'dev': ['data/dev-init.sh']},
    entry_points={
        'console_scripts': [
            'dev-bare = dev.cli:main',
        ],
    },
)
