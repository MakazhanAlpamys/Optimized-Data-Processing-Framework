import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import dask.array as da
import matplotlib.pyplot as plt

# Dictionary for simple caching
cache = {}

# Cache results
def cache_result(key, value):
    cache[key] = value

def get_cached_result(key):
    return cache.get(key)

# Generate a large dataset
data = np.random.randint(0, 1000000, size=(1000000,)).tolist()  # Testing with 1 million numbers

# Basic sorting (without optimization)
def basic_sort(data):
    return sorted(data)

# Basic statistics (without optimization)
def basic_summary(data):
    mean = np.mean(data)
    median = np.median(data)
    std_dev = np.std(data)
    return mean, median, std_dev

# Multithreaded sorting and statistics
def threaded_sort(data):
    chunk_size = len(data) // 4
    chunks = [data[i * chunk_size:(i + 1) * chunk_size] for i in range(4)]
    
    with ThreadPoolExecutor() as executor:
        sorted_chunks = list(executor.map(sorted, chunks))
    
    result = []
    for chunk in sorted_chunks:
        result.extend(chunk)
    return sorted(result)

# Multithreaded statistics
def threaded_summary(data):
    with ThreadPoolExecutor(max_workers=3) as executor:
        mean_future = executor.submit(np.mean, data)
        median_future = executor.submit(np.median, data)
        std_dev_future = executor.submit(np.std, data)
        
        mean = mean_future.result()
        median = median_future.result()
        std_dev = std_dev_future.result()
        
    return mean, median, std_dev

# Dask sorting (updated version)
def dask_sort(data):
    # Convert data to a NumPy array
    np_data = np.array(data)
    ddf = da.from_array(np_data, chunks=len(np_data) // 4)  # Use da.from_array from dask.array
    sorted_ddf = ddf.map_blocks(np.sort).compute()  # map_blocks applies sorting to each chunk
    return sorted_ddf

# Helper function to measure execution time and cache results
def measure_time(func, data, cache_key=None):
    if cache_key:
        cached_result = get_cached_result(cache_key)
        if cached_result:
            print(f"Cached result used for {func.__name__}")
            return cached_result
    
    start = time.time()
    result = func(data)
    duration = time.time() - start
    print(f"{func.__name__} took {duration:.4f} seconds")
    
    if cache_key:
        cache_result(cache_key, duration)
    
    return duration

# Performance comparison
results = {
    "Basic Sort": measure_time(basic_sort, data, "basic_sort"),
    "Threaded Sort": measure_time(threaded_sort, data, "threaded_sort"),
    "Dask Sort": measure_time(dask_sort, data, "dask_sort"),
    "Basic Summary": measure_time(basic_summary, data, "basic_summary"),
    "Threaded Summary": measure_time(threaded_summary, data, "threaded_summary"),
}

# Visualizing results
plt.figure(figsize=(12, 6))
plt.bar(results.keys(), results.values())
plt.ylabel("Execution Time (in seconds)")
plt.title("Performance Comparison of Different Optimizations")
plt.xticks(rotation=45)
plt.show()
