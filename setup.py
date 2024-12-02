from setuptools import setup, find_packages

setup(
    name="process-viewer",
    version="0.1.0",
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
    python_requires=">=3.11",
)
