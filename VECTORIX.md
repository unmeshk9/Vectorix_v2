# FloorPlanVectorizer

A comprehensive solution for converting raster floor plan images to vector format with structural element detection, optimized for office and commercial building floor plans.

![Floor Plan Vectorization Example](https://drive.google.com/file/d/1pm6PY7xZB6356MEYUqRM1VVR_fpjciW6/view?usp=sharing)

## Overview

FloorPlanVectorizer is built on the asf_floorplan_interpreter architecture (MIT License), leveraging YOLOv8-based instance segmentation to detect and vectorize structural elements (walls, doors, windows) from floor plan images. The system is designed specifically for commercial office environments, with a focus on accuracy and robust performance.

## Key Features

- **Structural Element Detection**: Precisely identifies walls, doors, and windows
- **Advanced Post-Processing**: Converts raw detections to clean vector data
- **Office-Optimized**: Designed specifically for commercial floor plans
- **Commercial-Ready**: Built on MIT-licensed components for commercial use
- **.NET Core Integration**: Python backend with .NET Core client for seamless integration
- **Production-Quality**: Engineered for robustness, speed, and accuracy

## Architecture

### Core Components

```
FloorPlanVectorizer/
├── model/
│   └── yolo_models/      # YOLOv8 model weights 
├── src/
│   ├── preprocessing/     # Image preprocessing
│   ├── detection/         # YOLOv8-based element detection
│   ├── postprocessing/    # Refinement and vectorization
│   ├── vectorization/     # Vector format conversion
│   └── dotnet/            # .NET Core integration 
├── api/                   # FastAPI REST service
└── README.md
```

### Detection Pipeline

```
Input Image → Preprocessing → YOLOv8 Detection → Post-Processing → Vectorization → JSON Output
```

## Post-Processing Pipeline

The heart of the system is an advanced post-processing pipeline that transforms raw model predictions into clean, usable vector data:

### 1. Mask Refinement and Noise Removal

Raw detection masks are refined through a series of morphological operations to remove noise and improve boundary precision:

```python
def refine_masks(masks, confidence_threshold=0.5):
    """Clean up prediction masks by removing noise and low-confidence regions."""
    refined_masks = []
    for mask, confidence in masks:
        if confidence < confidence_threshold:
            continue
            
        # Remove small isolated regions (noise)
        refined = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))
        
        # Fill small holes
        refined = cv2.morphologyEx(refined, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
        
        refined_masks.append(refined)
    
    return refined_masks
```

### 2. Wall Extraction and Straightening

Walls are extracted and processed to create clean, straight line segments suitable for CAD systems:

```python
def extract_and_straighten_walls(masks, floor_plan_image):
    """Extract wall contours and straighten them into line segments."""
    # Extract edges from masks
    edges = cv2.Canny(np.uint8(masks['wall']*255), 50, 150)
    
    # Use Hough transform to detect lines
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=20)
    
    # Merge collinear segments
    merged_lines = merge_collinear_lines(lines)
    
    # Snap lines to orthogonal grid (most office walls are at 90° angles)
    orthogonal_lines = snap_to_orthogonal(merged_lines)
    
    return orthogonal_lines
```

### 3. Door and Window Processing

Doors and windows are processed and aligned to the nearest walls for architectural correctness:

```python
def process_openings(door_masks, window_masks, wall_lines):
    """Process doors and windows to align them with walls."""
    doors = []
    windows = []
    
    # Process door masks
    for door_mask in door_masks:
        # Find door contour
        contours, _ = cv2.findContours(door_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Find minimum area rectangle
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            
            # Find nearest wall and snap door to it
            door_data = snap_opening_to_wall(box, wall_lines, opening_type="door")
            doors.append(door_data)
    
    # Similar process for windows
    # ...
    
    return doors, windows
```

### 4. Topology Graph Construction

A graph representation captures the topological relationships between structural elements:

```python
def build_topology_graph(walls, doors, windows):
    """Build a graph representing the topology of the floor plan."""
    G = nx.Graph()
    
    # Add walls as edges
    for i, wall in enumerate(walls):
        G.add_edge(f"p{wall[0]}", f"p{wall[1]}", type="wall", id=f"w{i}")
    
    # Add doors and windows as properties of walls
    for i, door in enumerate(doors):
        wall_id = door["wall_id"]
        G.edges[wall_id]["doors"] = G.edges[wall_id].get("doors", []) + [f"d{i}"]
    
    # Similar for windows
    # ...
    
    return G
```

### 5. Vectorization for CAD Integration

The final step converts all processed elements to a structured vector format suitable for CAD software:

```python
def vectorize_floor_plan(walls, doors, windows):
    """Convert processed elements to vector format suitable for CAD."""
    vector_data = {
        "walls": [],
        "doors": [],
        "windows": []
    }
    
    # Convert walls to line segments
    for wall in walls:
        start_point, end_point = wall["points"]
        thickness = wall["thickness"]
        vector_data["walls"].append({
            "start_x": float(start_point[0]),
            "start_y": float(start_point[1]),
            "end_x": float(end_point[0]),
            "end_y": float(end_point[1]),
            "thickness": float(thickness)
        })
    
    # Convert doors to vector representation
    for door in doors:
        # Convert door to vector format
        # ...
        
    # Similar for windows
    # ...
    
    return vector_data
```

## Integration with .NET Core

### REST API Approach

The system exposes its functionality through a RESTful API, making it easy to integrate with .NET Core applications:

```csharp
// C# client code
public class FloorPlanProcessor
{
    private readonly HttpClient _client;
    private readonly string _apiUrl;
    
    public FloorPlanProcessor(string apiUrl)
    {
        _client = new HttpClient();
        _apiUrl = apiUrl;
    }
    
    public async Task<FloorPlanElements> ProcessFloorPlanAsync(string imagePath)
    {
        using var content = new MultipartFormDataContent();
        using var imageContent = new ByteArrayContent(File.ReadAllBytes(imagePath));
        
        content.Add(imageContent, "image", Path.GetFileName(imagePath));
        
        var response = await _client.PostAsync($"{_apiUrl}/process", content);
        response.EnsureSuccessStatusCode();
        
        var result = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<FloorPlanElements>(result);
    }
}
```

### Alternative: Python.NET Integration

For applications requiring tighter integration, Python.NET offers direct invocation of the Python code from C#:

```csharp
public class FloorPlanDirectProcessor
{
    private dynamic _pyScope;
    
    public FloorPlanDirectProcessor()
    {
        // Initialize Python.NET
        Runtime.PythonDLL = "path/to/python311.dll";
        PythonEngine.Initialize();
        
        // Import modules
        _pyScope = PythonEngine.CreateScope();
        _pyScope.Execute(@"
            import sys
            sys.path.append('path/to/floorplan_vectorizer')
            from src.detection.predictor import FloorplanPredictor
            from src.postprocessing.pipeline import post_process_floor_plan
        ");
    }
    
    public FloorPlanElements ProcessFloorPlan(string imagePath)
    {
        // Process floor plan using Python code
        dynamic result = _pyScope.Execute($@"
            predictor = FloorplanPredictor(labels_to_predict=['WINDOW', 'DOOR'])
            predictor.load()
            prediction = predictor.predict_labels('{imagePath}')
            result = post_process_floor_plan(prediction, '{imagePath}')
            result
        ");
        
        // Convert Python result to C# object
        return ConvertToCSharpObject(result);
    }
}
```

## JSON Output Format

The system generates a clean, structured JSON output that can be directly used in CAD applications:

```json
{
  "walls": [
    {
      "id": 1,
      "start_x": 100.5,
      "start_y": 200.3,
      "end_x": 300.8,
      "end_y": 200.3,
      "thickness": 8.5
    }
  ],
  "doors": [
    {
      "id": 1,
      "wall_id": 1,
      "position_x": 200.4,
      "position_y": 200.3,
      "width": 80.0,
      "orientation": 90.0
    }
  ],
  "windows": [
    {
      "id": 1,
      "wall_id": 1,
      "position_x": 250.2,
      "position_y": 200.3,
      "width": 120.0,
      "orientation": 0.0
    }
  ],
  "metadata": {
    "image_size": [800, 600],
    "units": "pixels",
    "scale": 1.0,
    "processing_time": 0.856
  }
}
```

## Dependencies

### Python Dependencies
- YOLOv8 (Ultralytics)
- NumPy
- OpenCV
- NetworkX (for topology graph)
- FastAPI (for REST service)
- Python 3.9+

### .NET Dependencies
- .NET Core 6.0+ / .NET 7.0+
- System.Net.Http
- System.Text.Json
- (Optional) Python.NET for direct integration

## Implementation Steps

1. **Set Up Core Detection System**
   - Clone asf_floorplan_interpreter repository
   - Configure for structural elements only (walls, doors, windows)
   - Test with sample office floor plans

2. **Implement Post-Processing Pipeline**
   - Develop mask refinement functions
   - Create wall extraction and straightening logic
   - Build door and window processing
   - Implement topology graph construction
   - Create vectorization utilities

3. **Build REST API Service**
   - Develop FastAPI endpoints
   - Add error handling and validation
   - Implement caching and performance optimizations

4. **Create .NET Client**
   - Develop HTTP client for REST API
   - Implement response parsing and object mapping
   - Add error handling and resilience

5. **Testing and Validation**
   - Test with diverse office floor plans
   - Validate vectorization accuracy
   - Benchmark performance
   - Implement unit and integration tests

## Performance Considerations

- **Batch Processing**: Support for processing multiple floor plans in batch
- **Caching**: Implementation of result caching for repeat processing
- **Scaling**: Horizontal scaling of the REST API for high-volume applications
- **Hardware Acceleration**: GPU support for YOLOv8 inference when available

## License

FloorPlanVectorizer is released under the MIT License, making it suitable for commercial applications.

The core detection system is based on asf_floorplan_interpreter by Nesta, which is also released under the MIT License.

## Acknowledgments

- Based on asf_floorplan_interpreter by Nesta (MIT License)
- YOLOv8 by Ultralytics
- OpenCV for image processing functions
