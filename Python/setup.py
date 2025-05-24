from setuptools import setup, find_packages

setup(
    name='ocr_image_processing',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'numpy',
        'paddleocr',
	'paddlePaddle',
        'IPython',
        'matplotlib',  # Optional, if needed for additional image display handling
    ],
    entry_points={
        'console_scripts': [
            'ocr-image-processing=ocr_image_processing.main:main',  # Update this if you want to run the script as a command-line tool
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A script to process images and extract text using OCR.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/kumarpichandi05/PythonCaptcha",  # Update with your repository URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License=MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Adjust the required Python version if needed
)
