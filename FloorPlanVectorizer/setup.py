from setuptools import setup, find_packages

setup(
    name="floorplan_vectorizer",
    version="0.1.0",
    description="A comprehensive solution for converting raster floor plan images to vector format",
    author="Vectorix",
    packages=find_packages(),
    install_requires=[
        'ultralytics>=8.0.0',
        'numpy>=1.20.0',
        'opencv-python>=4.5.0',
        'networkx>=2.5',
        'fastapi>=0.68.0',
        'uvicorn>=0.15.0',
        'python-multipart>=0.0.5',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.9',
)
