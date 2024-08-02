# DataSampler
DataSampler is a Python package designed to sample time-based measurement data from medical devices into regular intervals.

## Features
- Sample measurements into regular intervals
- Configurable sampling interval
- Flexible starting time for sampling
- Comprehensive unit tests

## Installation
To install the package, clone the repository and install the dependencies:
```bash
git clone https://github.com/tejas7777/data-sampler.git
cd datasampler
pip install -r requirements.txt
```
## Usage
### Example
```python
from datasampler.measurement import Measurement, MeasType
from datasampler.sampler import DataSampler
from datetime import datetime

# creating a list of measurements
measurements = [
    Measurement(datetime.strptime('2017-01-03T10:04:45', '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.79),
    Measurement(datetime.strptime('2017-01-03T10:01:18', '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 98.78),
    Measurement(datetime.strptime('2017-01-03T10:09:07', '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.01),
    Measurement(datetime.strptime('2017-01-03T10:03:34', '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 96.49),
    Measurement(datetime.strptime('2017-01-03T10:02:01', '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.82),
    Measurement(datetime.strptime('2017-01-03T10:05:00', '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 97.17),
    Measurement(datetime.strptime('2017-01-03T10:05:01', '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 95.08),
]

# Init the DataSampler with a 5 mins interval
sampler = DataSampler(interval=5)

# samples the measurements
sampled_data = sampler.sample_measurements(measurements)

# Print the sampled data
DataSampler.print_data(sampled_data)
```
### Output
```terminal
{2017-01-03T10:05:00, SPO2, 97.17}
{2017-01-03T10:05:00, TEMP, 35.79}
{2017-01-03T10:10:00, SPO2, 95.08}
{2017-01-03T10:10:00, TEMP, 35.01}
```

### More Detailed Example
```python
# creating a list of measurements
measurements = [
    Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
    Measurement(datetime(2024, 1, 1, 10, 3), MeasType.TEMP, 36.5),
    Measurement(datetime(2024, 1, 1, 10, 7), MeasType.TEMP, 37.0),
]

# Initi the DataSampler with a 10 mins interval
sampler = DataSampler(interval=10)

# Sample the measurements with a custom interval
sampled_data = sampler.sample_measurements(measurements, interval=15)

# Print the sampled data
DataSampler.print_data(sampled_data)

# Sample the measurements with a custom start time
start_time = datetime(2024, 1, 1, 10, 5)
sampled_data_with_start = sampler.sample_measurements(measurements, start_of_sampling=start_time)
```

## Running Tests
Run the comprehensive tests using the below command
```bash
pytest -v
```

## Project Structure
Here is a brief overview of the files and directories in this project:
- `example.py`: Provides example usage of the DataSampler package.
- `setup.py`: Contains the metadata
- `datasampler/`: Directory containing the main package code.
  - `__init__.py`: Indicates that the directory is a Python package.
  - `measurement.py`: Defines the `Measurement` class and `MeasType` enumeration.
  - `sampler.py`: Implements the `DataSampler` class with methods for sampling measurements.
- `tests/`: Directory containing unit tests for the package.
  - `test_sampler.py`: Contains unit tests for the `DataSampler` class.

## Detailed File Descriptions
- **datasampler/measurement.py**:
  - Contains the `MeasType` enumeration which defines different types of measurements.
  - Defines the `Measurement` class which represents a single measurement, including the measurement time, type, and value.
  
- **datasampler/sampler.py**:
  - Implements the `DataSampler` class which provides methods for sampling measurements.
  - Includes utility methods like `sample_measurements`, `sample_measurements_by_type`, and utility methods for sorting and grouping measurements.
  
- **tests/test_sampler.py**:
  - Contains unit tests for the `DataSampler` class to ensure its methods work as expected.
  - Tests cover various scenarios including different intervals, starting times, and handling of empty or single measurement inputs.





