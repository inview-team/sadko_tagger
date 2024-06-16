from setuptools import setup, find_packages

setup(
    name='video_processing_pipeline',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'scenedetect[opencv]',
        'requests',
        'towhee',
        'opencv-python-headless'
    ],
    entry_points={
        'console_scripts': [
            'video_pipeline=pipeline.main_pipeline:video_processing_pipeline',
        ],
    },
)
