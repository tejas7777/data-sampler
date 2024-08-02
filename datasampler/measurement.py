from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MeasType(Enum):
    """Esnumeration of measurement types"""
    SPO2 = 1
    HR = 2
    TEMP = 3

@dataclass
class Measurement:
    """
    Represents a single measurement.

    Attributes:
        measurement_time (datetime): The time of measurement.
        measurement_type (MeasType): The type of measurement (SPO2, HR, TEMP).
        value (float): The numeric value of the measurement.
    """
    measurement_time: datetime = datetime.min
    measurement_type: MeasType = MeasType.SPO2
    value: float = 0.0

    def __post_init__(self):
        """
        Removes the microsecond from the measurement
        """
        self.measurement_time = self.measurement_time.replace(microsecond=0)

    def __str__(self):
        """
        Returns a string representation of the measurement.

        Returns:
            str: A string in the format "{measurement_time, measurement_type, value}
        """
        return f"{self.measurement_time.isoformat()}, {self.measurement_type.name}, {self.value:.2f}"
    
    