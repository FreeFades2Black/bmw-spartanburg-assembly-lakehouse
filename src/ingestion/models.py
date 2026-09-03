"""
BMW Plant Spartanburg Multi-Powertrain Assembly & AIQX Lakehouse
Pydantic Data Models & Facility Constants (src/ingestion/models.py)
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class PowertrainType(str, Enum):
    ICE = "ICE"       # Internal Combustion Engine (Gasoline / TwinPower Turbo)
    PHEV = "PHEV"     # Plug-in Hybrid Electric Vehicle (e.g. X5 xDrive50e)
    BEV = "BEV"       # Battery Electric Vehicle (e.g. iX5 / Neue Klasse 800V)


class VehicleModel(str, Enum):
    X3 = "BMW X3"
    X4 = "BMW X4"
    X5 = "BMW X5"
    X6 = "BMW X6"
    X7 = "BMW X7"
    XM = "BMW XM (High-Performance PHEV)"
    IX5 = "BMW iX5 Hydrogen/BEV"


class AssemblyHall(str, Enum):
    HALL_52 = "Assembly Hall 52 (Mid/Full-Size SAC/SAV: X5, X6, X7, XM, iX5)"
    HALL_50 = "Assembly Hall 50 (Compact SAC/SAV: X3, X4)"


class AssemblyStation(str, Enum):
    S01_CHASSIS_INTAKE = "L1_S01_CHASSIS_INTAKE"
    S05_UNDERBODY_PREP = "L1_S05_UNDERBODY_PREP"
    S12_BATTERY_MARRIAGE = "L1_S12_BATTERY_MARRIAGE"       # 800V Cell-to-Pack automated multi-spindle bolting
    S18_POWERTRAIN_DROP = "L1_S18_POWERTRAIN_DROP"         # ICE Engine & Transmission crane drop
    S24_EXHAUST_AND_HV_CABLING = "L1_S24_EXHAUST_AND_HV"   # Dual-path exhaust vs high-voltage orange cabling
    S32_DOORS_AND_INTERIOR = "L1_S32_DOORS_AND_INTERIOR"   # Cockpit and seating installation
    S40_GLAZING_AND_SEALING = "L1_S40_GLAZING_AND_SEALING" # Windshield bonding & vision inspection
    S50_FINAL_LINE_ROLLOFF = "L1_S50_FINAL_LINE_ROLLOFF"   # End-of-line dyno and electrical verification


class QuarantineStatus(str, Enum):
    PASSED = "PASSED"
    WARNING_DRIFT = "WARNING_DRIFT"
    QUARANTINED_AT_STATION = "QUARANTINED_AT_STATION"
    OFFLINE_REWORK_SHUNT = "OFFLINE_REWORK_SHUNT"


class StationSpecification(BaseModel):
    station_code: AssemblyStation
    station_name: str
    nominal_takt_ice_sec: float
    nominal_takt_phev_sec: float
    nominal_takt_bev_sec: float
    critical_sensors: List[str]
    max_buffer_capacity: int = 4


# Real BMW Spartanburg Multi-Station Line Configuration (Hall 52)
SPARTANBURG_HALL_52_STATIONS: Dict[str, StationSpecification] = {
    AssemblyStation.S01_CHASSIS_INTAKE.value: StationSpecification(
        station_code=AssemblyStation.S01_CHASSIS_INTAKE,
        station_name="Skid Infeed & RFID Chassis Induction",
        nominal_takt_ice_sec=48.0,
        nominal_takt_phev_sec=50.0,
        nominal_takt_bev_sec=52.0,
        critical_sensors=["RFID_TAG_RSSI", "SKID_ELEVATION_MM", "LASER_PROFILE_ALIGN_MM"]
    ),
    AssemblyStation.S05_UNDERBODY_PREP.value: StationSpecification(
        station_code=AssemblyStation.S05_UNDERBODY_PREP,
        station_name="Underbody Structural Prep & Anti-Corrosion Sealing",
        nominal_takt_ice_sec=54.0,
        nominal_takt_phev_sec=58.0,
        nominal_takt_bev_sec=62.0,
        critical_sensors=["DISPENSER_PRESSURE_BAR", "SEAL_BEAD_WIDTH_MM", "NOZZLE_TEMP_C"]
    ),
    AssemblyStation.S12_BATTERY_MARRIAGE.value: StationSpecification(
        station_code=AssemblyStation.S12_BATTERY_MARRIAGE,
        station_name="Plant Woodruff 800V Battery Marriage & Multi-Spindle Bolting",
        nominal_takt_ice_sec=32.0,  # Bypass / minimal skid transit
        nominal_takt_phev_sec=64.0, # 18-bolt high-voltage enclosure
        nominal_takt_bev_sec=74.0,  # 32-bolt structural pack + thermal gap filler
        critical_sensors=["SPINDLE_TORQUE_NM", "SPINDLE_ANGLE_DEG", "THERMAL_PASTE_VOL_ML", "GAP_PAD_COMPRESSION_KPA"]
    ),
    AssemblyStation.S18_POWERTRAIN_DROP.value: StationSpecification(
        station_code=AssemblyStation.S18_POWERTRAIN_DROP,
        station_name="Powertrain Marriage (ICE Engine Drop vs BEV Dual-E-Drive)",
        nominal_takt_ice_sec=68.0,  # Full 6-cyl / V8 engine crane drop & subframe mount
        nominal_takt_phev_sec=72.0, # Engine + electric motor hybrid module
        nominal_takt_bev_sec=46.0,  # Dual e-motor subframe bolt
        critical_sensors=["HOIST_LOAD_CELL_KG", "BOLT_TENSION_KN", "DRIVESHAFT_RUNOUT_UM"]
    ),
    AssemblyStation.S24_EXHAUST_AND_HV_CABLING.value: StationSpecification(
        station_code=AssemblyStation.S24_EXHAUST_AND_HV_CABLING,
        station_name="Exhaust Line Assembly & 800V High-Voltage Harnessing",
        nominal_takt_ice_sec=62.0,  # Exhaust hangers, catalytic converter, heat shields
        nominal_takt_phev_sec=66.0, # Exhaust + intermediate orange HV harness
        nominal_takt_bev_sec=44.0,  # High-voltage orange busbar click-in only (no exhaust)
        critical_sensors=["HV_CONTINUITY_OHMS", "EXHAUST_CLEARANCE_MM", "INTERLOCK_RESISTANCE_KOHM"]
    ),
    AssemblyStation.S32_DOORS_AND_INTERIOR.value: StationSpecification(
        station_code=AssemblyStation.S32_DOORS_AND_INTERIOR,
        station_name="Cockpit Marriage, Curved Display & High-Voltage Interlock",
        nominal_takt_ice_sec=56.0,
        nominal_takt_phev_sec=58.0,
        nominal_takt_bev_sec=60.0,
        critical_sensors=["COCKPIT_ROBOT_TORQUE_NM", "CAN_BUS_PING_MS", "HV_MANUAL_DISCONNECT_STATUS"]
    ),
    AssemblyStation.S40_GLAZING_AND_SEALING.value: StationSpecification(
        station_code=AssemblyStation.S40_GLAZING_AND_SEALING,
        station_name="Automated Panoramic Roof & Windshield Polyurethane Dispense",
        nominal_takt_ice_sec=52.0,
        nominal_takt_phev_sec=52.0,
        nominal_takt_bev_sec=54.0,
        critical_sensors=["GLAZING_ROBOT_PRESSURE_PSI", "VISION_BEAD_GAP_MM", "CURE_HUMIDITY_PCT"]
    ),
    AssemblyStation.S50_FINAL_LINE_ROLLOFF.value: StationSpecification(
        station_code=AssemblyStation.S50_FINAL_LINE_ROLLOFF,
        station_name="End-of-Line Roller Dyno, E/E Diagnostics & ADAS Calibration",
        nominal_takt_ice_sec=58.0,
        nominal_takt_phev_sec=64.0,
        nominal_takt_bev_sec=66.0,
        critical_sensors=["DYNO_SPEED_KPH", "HIGH_VOLTAGE_INSULATION_MOHM", "ADAS_RADAR_YAW_MRAD"]
    )
}


class ChassisRecord(BaseModel):
    vin: str
    sequence_no: int
    vehicle_model: VehicleModel
    powertrain_type: PowertrainType
    assembly_hall: AssemblyHall = AssemblyHall.HALL_52
    jis_battery_batch_id: Optional[str] = None
    jis_exhaust_batch_id: Optional[str] = None
    current_station: AssemblyStation
    actual_cycle_time_sec: float
    target_takt_time_sec: float
    quarantine_status: QuarantineStatus = QuarantineStatus.PASSED
    scrap_risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
