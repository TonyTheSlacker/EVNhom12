# Optimization Notes

This document contains notes on potential performance optimizations for future consideration.

## Current Performance Considerations

### 1. Haversine Coordinate Validation (file.py)

**Current Implementation:**
- Coordinate validation is performed on every haversine calculation
- Adds a small overhead to each distance calculation

**Potential Optimization:**
- Move validation to calling functions (validate once at input)
- Make validation optional with a parameter (e.g., `validate=True`)
- Use assertion-based validation that can be disabled with Python's -O flag

**Example:**
```python
def haversine(lat1: float, lng1: float, lat2: float, lng2: float, validate: bool = True) -> float:
    if validate:
        # validation code here
        pass
    # calculation code
```

**Impact:**
- Low priority - validation overhead is minimal compared to algorithm complexity
- Consider only if profiling shows this as a bottleneck

### 2. Recursive Theme Application (main.py)

**Current Implementation:**
- Theme is applied recursively to all widgets in the widget tree
- Called on every theme toggle

**Potential Optimization:**
- Cache widget types and references during initialization
- Implement iterative traversal instead of recursive
- Only update widgets that actually changed

**Example:**
```python
def __init__(self):
    self.themeable_widgets = []
    # During widget creation:
    self.themeable_widgets.append(('label', widget))
    
def apply_theme(self, theme):
    for widget_type, widget in self.themeable_widgets:
        # Apply theme based on cached type
```

**Impact:**
- Low priority - UI has relatively few widgets
- Theme toggle is infrequent user action
- Current implementation is more maintainable

### 3. Algorithm Performance

**Current Implementation:**
- A* and UCS limit candidate stations to 10 nearest per step
- Timeout set to 600 seconds (10 minutes)

**Potential Optimizations:**

#### A. Spatial Indexing
- Use KD-tree or R-tree for charging station lookups
- Reduces O(n) nearest neighbor search to O(log n)

```python
from scipy.spatial import cKDTree

# Build once during initialization
coords = df_charge[['lat', 'lng']].values
tree = cKDTree(coords)

# Query for nearest stations
distances, indices = tree.query([lat, lng], k=10)
```

#### B. Caching
- Cache haversine distances between frequently accessed station pairs
- Cache route segments for similar queries

#### C. Parallel Processing
- Process multiple candidate routes in parallel
- Use multiprocessing for independent path evaluations

#### D. Heuristic Improvements
- Improve A* heuristic to better estimate remaining distance
- Add domain-specific knowledge (e.g., highway routes)

**Impact:**
- Medium priority - algorithms can be slow for long routes
- Consider if user complaints about performance

### 4. Data Loading

**Current Implementation:**
- CSV files loaded on every application start
- No caching between sessions

**Potential Optimization:**
- Cache parsed CSV data
- Use binary format (pickle, parquet) for faster loading
- Lazy load data only when needed

**Impact:**
- Low priority - CSV files are small
- Loading time is negligible

### 5. Memory Usage

**Current Implementation:**
- Keeps all charging stations in memory
- Visited states dictionary can grow large

**Potential Optimization:**
- Stream process large datasets
- Implement memory limits for visited states
- Use generator patterns where possible

**Impact:**
- Low priority - current data size is manageable

## Profiling Tools

To identify actual bottlenecks, use Python profiling tools:

```bash
# cProfile - built-in profiler
python -m cProfile -o profile.stats main.py

# View results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"

# line_profiler - line-by-line profiling
pip install line_profiler
kernprof -l -v file.py

# memory_profiler - memory usage
pip install memory_profiler
python -m memory_profiler main.py
```

## When to Optimize

**Optimization should be considered when:**
1. Users report performance issues
2. Profiling identifies clear bottlenecks
3. Dataset size increases significantly
4. New features impact performance

**Current Status:**
- Application performs adequately for current use case
- Premature optimization should be avoided
- Focus on correctness and maintainability first

## Notes

- "Premature optimization is the root of all evil" - Donald Knuth
- Always profile before optimizing
- Optimize the hot path, not everything
- Maintain code readability when optimizing
- Document any non-obvious optimizations
