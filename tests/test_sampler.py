import unittest
from datetime import datetime
from datasampler.measurement import Measurement, MeasType
from datasampler.sampler import DataSampler
import io
import sys

class TestDataSampler(unittest.TestCase):

    def setUp(self):
        self.sampler = DataSampler()

    def test_init(self):
        self.assertEqual(self.sampler.interval, 5)
        with self.assertRaises(ValueError):
            DataSampler(interval=0)
        with self.assertRaises(ValueError):
            DataSampler(interval=-1)
        with self.assertRaises(ValueError):
            DataSampler(interval=None)

    def test_get_interval_start(self):
        time = datetime(2024, 1, 1, 10, 7, 30)
        expected = datetime(2024, 1, 1, 10, 5, 0)
        self.assertEqual(self.sampler._get_interval_start(time), expected)

    def test_sort_and_filter_measurements(self):
        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 2), MeasType.TEMP, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 3), MeasType.TEMP, 37.0),
        ]
        sorted_measurements = self.sampler._sort_and_filter_measurements(measurements, None)
        self.assertEqual(sorted_measurements[0].measurement_time, datetime(2024, 1, 1, 10, 1))
        self.assertEqual(sorted_measurements[-1].measurement_time, datetime(2024, 1, 1, 10, 3))

        filtered_measurements = self.sampler._sort_and_filter_measurements(measurements, datetime(2024, 1, 1, 10, 2))
        self.assertEqual(len(filtered_measurements), 2)
        self.assertEqual(filtered_measurements[0].measurement_time, datetime(2024, 1, 1, 10, 2))

    def test_group_measurements_by_type(self):
        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 2), MeasType.SPO2, 98.0),
            Measurement(datetime(2024, 1, 1, 10, 3), MeasType.TEMP, 37.0),
        ]
        grouped = self.sampler._group_measurements_by_type(measurements)
        self.assertEqual(len(grouped[MeasType.TEMP]), 2)
        self.assertEqual(len(grouped[MeasType.SPO2]), 1)

    def test_sample_single_type(self):
        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 3), MeasType.TEMP, 36.5),
            Measurement(datetime(2024, 1, 1, 10, 7), MeasType.TEMP, 37.0),
        ]
        sampled = self.sampler._sample_single_type(MeasType.TEMP, measurements)
        self.assertEqual(len(sampled), 2)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[0].value, 36.5)
        self.assertEqual(sampled[1].measurement_time, datetime(2024, 1, 1, 10, 10))
        self.assertEqual(sampled[1].value, 37.0)

    def test_sample_measurements(self):
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
        sampled = self.sampler.sample_measurements([])
        self.assertEqual(len(sampled), 0)

    def test_sample_measurements_single_measurement(self):
        measurements = [Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0)]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 1)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[0].value, 36.0)

    def test_sample_measurements_multiple_in_same_interval(self):
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
        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 10), MeasType.SPO2, 36.5),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        DataSampler.print_data(sampled)
        self.assertEqual(len(sampled), 2)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[0].value, 36.0)
        self.assertEqual(sampled[1].measurement_time, datetime(2024, 1, 1, 10, 5))
        self.assertEqual(sampled[1].value, 36.5)


    def test_sample_measurements_large_time_gap(self):
        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 0), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 11, 0), MeasType.TEMP, 36.5),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 2)
        self.assertEqual(sampled[0].measurement_time, datetime(2024, 1, 1, 10, 0))
        self.assertEqual(sampled[1].measurement_time, datetime(2024, 1, 1, 11, 0))

    def test_sample_measurements_multiple_types(self):
        measurements = [
            Measurement(datetime(2024, 1, 1, 10, 1), MeasType.TEMP, 36.0),
            Measurement(datetime(2024, 1, 1, 10, 2), MeasType.SPO2, 98.0),
            Measurement(datetime(2024, 1, 1, 10, 3), MeasType.HR, 70),
            Measurement(datetime(2024, 1, 1, 10, 7), MeasType.TEMP, 36.5),
        ]
        sampled = self.sampler.sample_measurements(measurements)
        self.assertEqual(len(sampled), 4)
        self.assertEqual(set(m.measurement_type for m in sampled), {MeasType.TEMP, MeasType.SPO2, MeasType.HR})

    def test_print_data_empty(self):
        captured_output = io.StringIO()
        sys.stdout = captured_output
        DataSampler.print_data([])
        sys.stdout = sys.__stdout__
        self.assertEqual(captured_output.getvalue(), "")

    def test_print_data_invalid_input(self):
        with self.assertRaises(TypeError):
            DataSampler.print_data("invalid input")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDataSampler)
    unittest.TextTestRunner(verbosity=2).run(suite)