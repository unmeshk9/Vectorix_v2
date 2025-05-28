# FloorPlanVectorizer

A comprehensive solution for converting raster floor plan images to vector format with structural element detection, optimized for office and commercial building floor plans.

## Overview

FloorPlanVectorizer is built on the asf_floorplan_interpreter architecture (MIT License), leveraging YOLOv8-based instance segmentation to detect and vectorize structural elements (walls, doors, windows) from floor plan images. The system is designed specifically for commercial office environments, with a focus on accuracy and robust performance.

## Key Features

- **Structural Element Detection**: Precisely identifies walls, doors, and windows
- **Advanced Post-Processing**: Converts raw detections to clean vector data
- **Office-Optimized**: Designed specifically for commercial floor plans
- **Commercial-Ready**: Built on MIT-licensed components for commercial use
- **.NET Core Integration**: Python backend with .NET Core client for seamless integration
- **Production-Quality**: Engineered for robustness, speed, and accuracy

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/FloorPlanVectorizer.git
cd FloorPlanVectorizer
```

2. Install the package and dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

## Usage

### Basic Usage

```python
from floorplan_vectorizer.src.detection.predictor import FloorplanPredictor
from floorplan_vectorizer.src.postprocessing.pipeline import post_process_floor_plan

# Initialize the predictor
predictor = FloorplanPredictor(labels_to_predict=['WINDOW', 'DOOR', 'WALL'])
predictor.load()

# Predict elements in a floor plan
image_path = 'path/to/floor_plan.png'
labels, label_counts = predictor.predict_labels(image_path)

# Process the predictions to generate vector data
vector_data = post_process_floor_plan(labels, image_path)

# Output to JSON
import json
with open('output.json', 'w') as f:
    json.dump(vector_data, f, indent=2)
```

### Using the API

1. Start the API server:

```bash
cd FloorPlanVectorizer
uvicorn floorplan_vectorizer.api.main:app --reload
```

2. Send a request using curl:

```bash
curl -X POST "http://localhost:8000/process" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@path/to/floor_plan.png"
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

## License

FloorPlanVectorizer is released under the MIT License, making it suitable for commercial applications.

The core detection system is based on asf_floorplan_interpreter by Nesta, which is also released under the MIT License.

## Acknowledgments

- Based on asf_floorplan_interpreter by Nesta (MIT License)
- YOLOv8 by Ultralytics
- OpenCV for image processing functions
