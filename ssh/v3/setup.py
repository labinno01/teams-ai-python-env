from setuptools import setup, find_packages

setup(
    name="sshkeys",
    version="3.0.0",
    author="Votre Nom",
    author_email="votre@email.com",
    description="Outil de gestion des clés SSH pour GitHub et serveurs",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/votre_utilisateur/votre_depot", # Replace with your GitHub repo URL
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        "click",
        "pyyaml",
        "pydantic",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "sshkeys = sshkeys.cli:cli",
        ],
    },
)
