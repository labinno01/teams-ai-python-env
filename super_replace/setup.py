from setuptools import setup, find_packages

setup(
    name="super_replace",
    version="0.1.0",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        "click",
        "astor",
    ],
    entry_points={
        "console_scripts": [
            "super_replace = super_replace.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
