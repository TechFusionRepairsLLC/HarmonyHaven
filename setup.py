from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="HarmonyHaven",
    version="1.5",  # Adhering to Semantic Versioning
    description="A music management and playback tool by TechFusion Repairs LLC",
    long_description=long_description,  # Optional, but recommended for PyPI
    long_description_content_type="text/markdown",  # Tells PyPI to expect markdown formatting
    author="Alejandro X. Solis",
    author_email="TechFusionRepairsLLC@gmail.com",
    url="https://github.com/TechFusionRepairs/HarmonyHaven",  # GitHub repo URL
    license="MIT",
    packages=find_packages(),  # Automatically finds and includes packages in your project
    include_package_data=True,  # Includes non-Python files specified in MANIFEST.in
    install_requires=[
        "pygame>=2.0.0",      # For handling audio and multimedia
        "mutagen>=1.45.1",    # For managing ID3 tags
        "pydub>=0.25.1",      # For manipulating audio files
        "Pillow>=9.0.0",      # For image handling
        "tkinter",            # For GUI (standard in most Python distributions)
    ],
    entry_points={
        'console_scripts': [
            'harmonyhaven=harmonyhaven:main',  # Updated if `main()` is inside a submodule
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",  # Indicating the development status
        "Intended Audience :: End Users/Desktop",  # Target audience
        "Topic :: Multimedia :: Sound/Audio",  # Relevant topic categories
    ],
    python_requires='>=3.6',  # Ensures compatibility with Python 3.6 and later
)

# Created by Alejandro X. Solis, Owner of TechFusion Repairs LLC
# MIT License
# Copyright (c) 2024 TechFusion Repairs LLC
# All Rights Reserved.
# See LICENSE file for more details.
# © 2024 TechFusion Repairs LLC. All rights reserved.