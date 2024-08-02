import unittest
import io
import sys
from datetime import datetime
from datasampler.measurement import Measurement, MeasType
from datasampler.sampler import DataSampler

class TestDataSampler(unittest.TestCase):
    """Unit tests for the DataSampler class."""

    def setUp(self):
        """Set up the test environment by initializing a DataSampler instance """

        self.sampler = DataSampler()

    def test_given_measurements_example(self):
        """Test sampling with provided example measurements"""

        measurements = [
            Measurement(datetime.strptime('2017-01-03T10:04:45',
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.79),
            Measurement(datetime.strptime('2017-01-03T10:01:18',
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 98.78),
            Measurement(datetime.strptime('2017-01-03T10:09:07',
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.01),
            Measurement(datetime.strptime('2017-01-03T10:03:34',
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 96.49),
            Measurement(datetime.strptime('2017-01-03T10:02:01',
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.82),
            Measurement(datetime.strptime('2017-01-03T10:05:00',
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 97.17),
            Measurement(datetime.strptime('2017-01-03T10:05:01', 
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 95.08),
        ]

        sampled = self.sampler.sample_measurements(measurements)

        DataSampler.print_data(sampled)

        expected_output = [
            Measurement(datetime.strptime('2017-01-03T10:05:00',
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 97.17),
            Measurement(datetime.strptime('2017-01-03T10:05:00',
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.79),
            Measurement(datetime.strptime('2017-01-03T10:10:00',
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.SPO2, 95.08),
            Measurement(datetime.strptime('2017-01-03T10:10:00', 
                                          '%Y-%m-%dT%H:%M:%S'), MeasType.TEMP, 35.01),
        ]

        self.assertEqual(len(sampled), len(expected_output))
        for actual, expected in zip(sampled, expected_output):
            self.assertEqual(actual.measurement_time, expected.measurement_time)
            self.assertEqual(actual.measurement_type, expected.measurement_type)
            self.assertEqual(actual.value, expected.value)

    def test_init(self):
        """Test the inits of DataSampler and validation of interval"""

        self.assertEqual(self.sampler.interval, 5)
        with self.assertRaises(ValueError):
            DataSampler(interval=0)
        with self.assertRaises(ValueError):
            DataSampler(interval=-1)
        with self.assertRaises(ValueError):
            DataSampler(interval=None)

    def test_sample_measurements(self):
        """Test sampling of measurements with simple intervals"""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 2), MeasType.SPO2, 98.0),
            Measurement(datetime(2024, 1, 1, 10, 3), MeasType.TEMP, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 7), MeasType.TEMP, 37.0),
            Measurement(datetime(2024, 1, 1, 10, 8), MeasType.SPO2, 99.0),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 4)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[0].measurement_type, MeasType.TEMP)
        self.assertEqual(sampled[0].value, 36.5)
        self.assertEqual(sampled[1].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[1].measurement_type, MeasType.SPO2)
        self.assertEqual(sampled[1].value, 98.0)

    def test_sample_measurements_with_new_interval(self):
        """Test sampling of measurements with a specified news interval"""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 3), MeasType.TEMP, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 7), MeasType.TEMP, 37.0),
        ]
        sampled = self.sampler.sample_measurements(measurements, interval=10)
        self.assertEqual(len(sampled), 1)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 10))
        self.assertEqual(sampled[0].value, 37.0)

    def test_sample_measurements_with_start_time(self):
        """Test sampling of measurements with a specified start time"""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 3), MeasType.TEMP, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 7), MeasType.TEMP, 37.0),
        ]
        start_time = datetime(2024, 1, 1, 10, 5)
        sampled = self.sampler.sample_measurements(measurements, start_of_sampling=start_time)
        self.assertEqual(len(sampled), 1)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 10))
        self.assertEqual(sampled[0].value, 37.0)

    def test_sample_measurements_unsorted(self):
        """Test sampling of unsorted measurements"""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 7), MeasType.TEMP, 37.0),
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 3), MeasType.TEMP, 36.5),
        ]
        sampled = self.sampler.sample_measurements(measurements, to_sort=False)
        self.assertEqual(len(sampled), 2)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[0].value, 36.5)
        self.assertEqual(sampled[1].measurement_time, datetime(2024, 1, 1, 10, 10))
        self.assertEqual(sampled[1].value, 37.0)

    def test_print_data_list(self):
        """Test printing of sampled data as a list"""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 5), MeasType.TEMP, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.SPO2, 98.0),
        ]
        captured_output = io.StringIO()
        sys.stdout = captured_output
        DataSampler.print_data(measurements)
        sys.stdout = sys.__stdout__
        expected_output = "{2024-01-01T10:05:00, TEMP, 36.50}\n{2024-01-01T10:10:00, SPO2, 98.00}\n"
        self.assertEqual(captured_output.getvalue(), expected_output)

    def test_print_data_dict(self):
        """Test printing of sampled data grouped by measurement types """

        measurements = {
            MeasType.TEMP: [
                Measurement(datetime(2024, 1, 1, 10, 5), MeasType.TEMP, 36.5),
                Measurement(datetime(2024, 1, 1, 10, 15), MeasType.TEMP, 36.7),
            ],
            MeasType.SPO2: [
                Measurement(datetime(2024, 1, 1, 10, 10), MeasType.SPO2, 98.0),
            ]
        }
        captured_output = io.StringIO()
        sys.stdout = captured_output
        DataSampler.print_data(measurements)
        sys.stdout = sys.__stdout__
        expected_output = (
            "Measurement Type: TEMP\n"
            "  {2024-01-01T10:05:00, 36.50}\n"
            "  {2024-01-01T10:15:00, 36.70}\n"
            "Measurement Type: SPO2\n"
            "  {2024-01-01T10:10:00, 98.00}\n"
        )
        self.assertEqual(captured_output.getvalue(), expected_output)

    def test_sample_measurements_empty_input(self):
        """Test sampling of an empty list of measurements"""

        sampled = self.sampler.sample_measurements([])
        self.assertEqual(len(sampled), 0)

    def test_sample_measurements_single_measurement(self):
        """Test sampling of a single measurement."""

        measurements = [Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0)]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 1)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[0].value, 36.0)

    def test_sample_measurements_multiple_in_same_interval(self):
        """Test sampling of multiple measurements in the same interval"""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 2), MeasType.TEMP, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 3), MeasType.TEMP, 37.0),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 1)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[0].value, 37.0)

    def test_sample_measurements_exact_time(self):
        """Test sampling of measurements that fall exactly on interval boundaries"""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.SPO2, 36.5),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 2)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 10))
        self.assertEqual(sampled[0].value, 36.0)
        self.assertEqual(sampled[1].measurement_time, datetime(2024, 1, 1, 10, 10))
        self.assertEqual(sampled[1].value, 36.5)

    def test_sample_measurements_boundary_time(self):
        """Test sampling of measurements at boundary times and multiple types."""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 7), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.TEMP, 36.1),
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.SPO2, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.HR, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 15), MeasType.HR, 36.7),
            Measurement(datetime(2024, 1, 1, 10, 25), MeasType.HR, 30.5),
        ]

        sampled = self.sampler.sample_measurements(measurements)

        DataSampler.print_data(sampled)

        expected_output = [
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.TEMP, 36.1),
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.SPO2, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.HR, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 15), MeasType.HR, 36.7),
            Measurement(datetime(2024, 1, 1, 10, 25), MeasType.HR, 30.5),
        ]

        self.assertEqual(len(sampled), len(expected_output))
        for actual, expected in zip(sampled, expected_output):
            self.assertEqual(actual.measurement_time, expected.measurement_time)
            self.assertEqual(actual.measurement_type, expected.measurement_type)
            self.assertEqual(actual.value, expected.value)

        # Additional checks for specific boundary conditions
        self.assertEqual(len([m for m in sampled
                              if m.measurement_time == datetime(2024, 1, 1, 10, 10)]), 3)
        self.assertTrue(any(m.measurement_type == MeasType.TEMP and
                            m.measurement_time == datetime(2024, 1, 1, 10, 10) for m in sampled))
        self.assertTrue(any(m.measurement_type == MeasType.SPO2 and
                            m.measurement_time == datetime(2024, 1, 1, 10, 10) for m in sampled))
        self.assertTrue(any(m.measurement_type == MeasType.HR and
                            m.measurement_time == datetime(2024, 1, 1, 10, 10) for m in sampled))

    def test_sample_measurements_large_time_gap(self):
        """Test sampling of measurements with a large time gap between them."""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 11, 1), MeasType.TEMP, 36.5),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        DataSampler.print_data(sampled)
        self.assertEqual(len(sampled), 2)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[1].measurement_time, datetime(2024, 1, 1, 11, 5))

    def test_sample_measurements_multiple_types(self):
        """Test sampling of measurements with multiple type"""
        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 2), MeasType.SPO2, 98.0),
            Measurement(datetime(2024, 1, 1, 10, 3), MeasType.HR, 70),
            Measurement(datetime(2024, 1, 1, 10, 7), MeasType.TEMP, 36.5),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 4)
        self.assertEqual(set(m.measurement_type for m in sampled),
                         {MeasType.TEMP, MeasType.SPO2, MeasType.HR})

    def test_measurements_on_interval_boundaries(self):
        """Test sampling of measurements exactly on interval boundaries"""
        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 0), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 5), MeasType.TEMP, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.HR, 37.0),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 3)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 0))
        self.assertEqual(sampled[1].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[2].measurement_time, datetime(2024, 1, 1, 10, 10))

    def test_rapid_succession_measurements(self):
        """Test sampling of measurements in rapid succession"""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 1, 2), MeasType.TEMP, 36.1),
            Measurement(datetime(2024, 1, 1, 10, 1, 3), MeasType.TEMP, 36.2),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 1)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[0].value, 36.2)

    def test_sparse_measurements(self):
        """Test sampling of sparse measurements"""

        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 11, 1), MeasType.HR, 36.5),
            Measurement(datetime(2024, 1, 1, 12, 1), MeasType.TEMP, 37.0),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 3)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[1].measurement_time, datetime(2024, 1, 1, 11, 5))
        self.assertEqual(sampled[2].measurement_time, datetime(2024, 1, 1, 12, 5))

    def test_print_data_empty(self):
        """Test printing of an empty list of measurements"""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        DataSampler.print_data([])
        sys.stdout = sys.__stdout__
        self.assertEqual(captured_output.getvalue(), "")

    def test_print_data_invalid_input(self):
        """Test printing with invalid input """

        with self.assertRaises(TypeError):
            DataSampler.print_data("invalid input")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataSampler)
    unittest.TextTestRunner(verbosity=2).run(suite)
