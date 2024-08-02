from typing import List, Optional, Union
from datetime import datetime, timedelta
from collections import defaultdict
from .measurement import Measurement, MeasType


class DataSampler:
    """
    A class for sampling time-based measurement data into regular intervals. 
    The class contains the core sampling logic and helper functions

    Attributes:
        interval (int): The sampling interval in minutes. Default is 5 minutes.

    Methods:
        sample_measurements(unsampled_measurements, interval=None, start_of_sampling=None):
            Sample measurements into regular intervals.
        
        (static) print_data(data):
            method that prints data

    Usage:
        >>> sampler = DataSampler(interval=5)
        >>> sampled_data = sampler.sample_measurements(unsampled_measurements)

    """

    def __init__(self, interval: int = 5):
        """
        Initialises the DataSampler class.

        Args:
            [Optional] interval_minuites (int): The interval to sample data based on.
        """

        if interval is None or interval <= 0:
            raise ValueError("Interval must be a positive integer")
        self.interval: int = interval


    def sample_measurements(self, unsampled_measurements: List[Measurement],
                        interval: Optional[int] = None, 
                        start_of_sampling: Optional[datetime] = None, 
                        to_sort: Optional[bool] = True) -> List[Measurement]:
        """
        Samples data based on the interval or a new interval provided during method invocation.
        
        Args:
            unsampled_measurements (List[Measurement]): A list of Measurement objects to be sampled.
            interval (int, optional): A new interval in minutes for sampling data, if provided.
            start_of_sampling (datetime, optional): The start datetime from which to begin sampling.
            to_sort (boolean, optional): To return sorted list based on datetime.

        Returns:
            List[Measurement]: A list of sampled Measurement objects 
            based on the specified interval.
        """

        if interval is not None and interval > 0:
            self.interval = interval

        sorted_measurements = self.__sort_and_filter_measurements(unsampled_measurements,
                                                                  start_of_sampling)
        intervals: set = self.__generate_intervals(sorted_measurements,
                                                   start_of_sampling)
        grouped_measurements = self.__group_measurements_by_type(sorted_measurements)
        
        sampled_measurements = []
        for meas_type, measurements in grouped_measurements.items():
            sampled_measurements.extend(
                self.__sample_single_type(meas_type, measurements, intervals)
                )

        if to_sort:
            return sampled_measurements

        return sampled_measurements
    
    def sample_measurements_by_type(self, unsampled_measurements: List[Measurement],
                                    interval: Optional[int] = None, 
                                    start_of_sampling: Optional[datetime] = None
                                ) -> dict[MeasType, list[Measurement]]:
        """
        Samples data and returns results grouped by measurement type.
        
        Args:
            unsampled_measurements (List[Measurement]): A list of Measurement Objects.
            interval (int, optional): A new interval in minutes.
            start_of_sampling (datetime, optional): The start datetime from which to begin sampling.

        Returns:
            dict[MeasType, list[Measurement]]: A dictionary with measurement types as keys and 
                                            lists of sampled Measurement objects as values.
        """
        if interval is not None and interval > 0:
            self.interval = interval

        sorted_measurements = self.__sort_and_filter_measurements(unsampled_measurements,
                                                                  start_of_sampling)
        intervals: set = self.__generate_intervals(sorted_measurements,
                                                   start_of_sampling)
        grouped_measurements = self.__group_measurements_by_type(sorted_measurements)

        sampled_measurements = {}
        for meas_type, measurements in grouped_measurements.items():
            sampled_measurements[meas_type] = self.__sample_single_type(meas_type, 
                                                                        measurements, intervals)

        return sampled_measurements

    def __get_interval_start(self, time: datetime) -> datetime:
        """
         [Private Method] Get the start time of the interval for a given timestamp.

        Args:
            time (datetime): The timestamp to find the interval end for.

        Returns:
            datetime: The end of the interval.
        """
        minutes = (time.minute // self.interval) * self.interval
        return time.replace(minute=minutes, second=0, microsecond=0)

    def __sort_and_filter_measurements(self, measurements: List[Measurement], 
                                       start_time: Optional[datetime]) -> List[Measurement]:
        """
        [Private Method] Sorts measurements by time and filters based on an optional start time.
        
        Args:
            measurements (List[Measurement]): A list of Measurement 
                objects to be sorted and filtered.
            start_time (datetime, optional): The start datetime from 
                which to include measurements.

        Returns:
            List[Measurement]: A list of sorted Measurement objects, 
                filtered if start_time is provided.
        """
        sorted_measurements = sorted(measurements, key=lambda m: m.measurement_time)
        if start_time:
            return [m for m in sorted_measurements if m.measurement_time >= start_time]
        return sorted_measurements

    def __group_measurements_by_type(self, measurements: List[Measurement]) -> dict[MeasType, List[Measurement]]:
        """
        [Private Method] Groups measurements by their measurement type.
        
        Args:
            measurements (List[Measurement]): A list of Measurement objects to be grouped.

        Returns:
            dict[MeasType, List[Measurement]]: A dictionary with measurement 
                types as keys and lists of 
            corresponding Measurement objects as values.
        """
        grouped = defaultdict(list)
        for measurement in measurements:
            grouped[measurement.measurement_type].append(measurement)
        return grouped

    def __sample_single_type(self, meas_type: MeasType, 
                             measurements: List[Measurement], 
                             intervals: set) -> List[Measurement]:
        """
        [Private Method] Samples measurements of a single type.

        Args:
            meas_type (MeasType): The type of measurement being sampled.
            measurements (List[Measurement]): A list of Measurement objects of the same type.

        Returns:
            List[Measurement]: A list of sampled Measurement objects, with one measurement
                                per interval, sorted by time.
        """


        sampled = []
        if not measurements:
            return sampled
 
        current_interval_end = self.__get_interval_start(measurements[0].measurement_time) \
                                + timedelta(minutes=self.interval)
        last_measurement = None

        for measurement in measurements:
            if measurement.measurement_time in intervals:
                sampled.append(Measurement(measurement.measurement_time, 
                                           meas_type, measurement.value))
                last_measurement = None
                continue

            while measurement.measurement_time > current_interval_end:
                if last_measurement:
                    sampled.append(Measurement(current_interval_end, 
                                               meas_type, last_measurement.value))
                    last_measurement = None
                current_interval_end += timedelta(minutes=self.interval)
            last_measurement = measurement

        if last_measurement:
            sampled.append(Measurement(current_interval_end, 
                                       meas_type, last_measurement.value))

        return sampled
   
    def __generate_intervals(self, measurements: List[Measurement], start_of_sampling: Optional[datetime] = None) -> set[datetime]:
        """
        [Private Method] Generates a list of interval start times based on the given measurements

        Args:
            measurements (List[Measurement]): A list of Measurement objects to 
                base the intervals on
            start_of_sampling (datetime, optional): The start datetime from which 
                to begin generating intervals

        Returns:
            List[datetime]: A list of datetime objects representing the start of each interval
        """
        if not measurements:
            return set()

        sorted_measurements = sorted(measurements, key=lambda m: m.measurement_time)
        start_time = start_of_sampling or self.__get_interval_start(sorted_measurements[0].measurement_time)
        end_time = sorted_measurements[-1].measurement_time

        intervals = []
        current_time = start_time
        while current_time <= end_time:
            intervals.append(current_time)
            current_time += timedelta(minutes=self.interval)

        return intervals

    @staticmethod
    def print_data(data: Union[List[Measurement], dict[MeasType, List[Measurement]]]):
        """
        [Static] Prints the sampled data in a readable format.

        Args:
            data (List[Measurement]): The sampled data to print.
        """
        if isinstance(data, list):
            for measurement in data:
                print(f"{{{measurement.measurement_time.isoformat()}, {measurement.measurement_type.name}, {measurement.value:.2f}}}")
        elif isinstance(data, dict):
            for meas_type, measurements in data.items():
                print(f"Measurement Type: {meas_type.name}")
                for measurement in measurements:
                    print(f"  {{{measurement.measurement_time.isoformat()}, {measurement.value:.2f}}}")
        else:
            raise TypeError("Input must be either a list of Measurements or List[Measurement]")
        