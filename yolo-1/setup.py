from setuptools import setup, find_packages

setup(
    name='yolo',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='YOLO-based vehicle detection and risk analysis system',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'torch',
        'opencv-python',
        'ultralytics',
        'numpy',
        'serial',
        'json',
        'pydantic',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'yolo=rhinomain:main',  # Assuming you have a main function in rhinomain.py
        ],
    },
)