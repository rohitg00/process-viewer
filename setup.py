from setuptools import setup, find_packages

setup(
    name="process-viewer",
    version="0.1.0",
    author="Rohit Ghumare",
    author_email="ghumare64@gmail.com",
    description="A terminal-based process visualization tool providing real-time system process monitoring and management capabilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rohitg00/process-viewer",
    project_urls={
        "Bug Tracker": "https://github.com/rohitg00/process-viewer/issues",
        "Source": "https://github.com/rohitg00/process-viewer",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "psutil>=6.1.0",
        "curses-menu>=0.7.0",
    ],
    entry_points={
        'console_scripts': [
            'process-viewer=process_viewer.main:run',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.11",
)
