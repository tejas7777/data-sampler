import random
from typing import List
from datetime import datetime, timedelta
from datasampler.sampler import DataSampler
from datasampler.measurement import Measurement, MeasType

def generate_measurements(num_measurements: int) -> List[Measurement]:
    """
    Generates a list of sample Measurement objects.

    Args:
        num_measurements (int): The number of Measurement objects to generate.

    Returns:
        List[Measurement]: A list of generated Measurement objects.
    """
    measurement_types = list(MeasType)
    start_time = datetime.now()
    measurements = []

    for _ in range(num_measurements):
        measurement_time = start_time + timedelta(seconds=random.randint(0, 3600))
        measurement_type = random.choice(measurement_types)
        value = round(random.uniform(90.0, 100.0) if measurement_type == MeasType.SPO2 else random.uniform(30.0, 40.0), 2)
        measurement = Measurement(measurement_time, measurement_type, value)
        measurements.append(measurement)

    return measurements

given_input = [
    Measurement(datetime.strptime('2017-01-03T10:04:45', '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.79),
    Measurement(datetime.strptime('2017-01-03T10:01:18', '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 98.78),
    Measurement(datetime.strptime('2017-01-03T10:09:07', '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.01),
    Measurement(datetime.strptime('2017-01-03T10:03:34', '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 96.49),
    Measurement(datetime.strptime('2017-01-03T10:02:01', '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.82),
    Measurement(datetime.strptime('2017-01-03T10:05:00', '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 97.17),
    Measurement(datetime.strptime('2017-01-03T10:05:01', '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 95.08),
]


if __name__ == '__main__':
    print("--------------Example 1: Given Input Data--------------")
    data_sampler = DataSampler(5)
    sampled_data = data_sampler.sample_measurements(given_input)
    sampled = data_sampler.sample_measurements(sampled_data)
    DataSampler.print_data( sampled )

    print("--------------Example 2: Generated Input Data Data--------------")
    generated_measurement = generate_measurements(100)
    DataSampler.print_data( data_sampler.sample_measurements(generated_measurement) )

    print("--------------Example 3: Sample Measurements by Type--------------")
    DataSampler.print_data( data_sampler.sample_measurements_by_type(generated_measurement) )

