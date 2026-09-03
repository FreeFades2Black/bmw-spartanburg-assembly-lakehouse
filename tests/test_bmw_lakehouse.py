"""
BMW Plant Spartanburg Multi-Powertrain Assembly & AIQX Lakehouse
Unit & Integration Test Suite (tests/test_bmw_lakehouse.py)
"""

import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.models import (
    PowertrainType,
    VehicleModel,
    AssemblyHall,
    AssemblyStation,
    SPARTANBURG_HALL_52_STATIONS
)
from src.ingestion.multi_station_stream_generator import SpartanburgMultiStationExtractor
from src.analytics.aiqx_defect_quarantine import BMWAIQXQuarantineEngine
from src.analytics.timesfm_takt_forecaster import TimesFM3TaktForecaster
from src.analytics.jis_logistics_optimizer import BMWJISLogisticsSynchronizer
from src.processing.delta_lakehouse import BMWSpartanburgLakehousePipeline


def test_models_and_station_specifications():
    """Verify multi-powertrain enum integrity and Hall 52 station configurations."""
    assert len(SPARTANBURG_HALL_52_STATIONS) == 8
    assert AssemblyStation.S12_BATTERY_MARRIAGE.value in SPARTANBURG_HALL_52_STATIONS
    
    s12 = SPARTANBURG_HALL_52_STATIONS[AssemblyStation.S12_BATTERY_MARRIAGE.value]
    assert s12.nominal_takt_bev_sec == 74.0
    assert s12.nominal_takt_ice_sec == 32.0
    assert "SPINDLE_TORQUE_NM" in s12.critical_sensors


def test_multi_station_bronze_silver_ingestion():
    """Verify multi-station telemetry generation, Bronze Delta ingestion, and Silver Mart creation."""
    extractor = SpartanburgMultiStationExtractor()
    raw_csv = extractor.generate_synthetic_telemetry(total_chassis=15)
    bronze_path = extractor.ingest_to_bronze(raw_csv)
    silver_path = extractor.build_silver_mart(bronze_path)

    assert bronze_path.exists()
    assert silver_path.exists()


def test_aiqx_early_defect_quarantine():
    """Verify AIQX early defect quarantine shunts excursions and prevents Station 50 teardown costs."""
    engine = BMWAIQXQuarantineEngine()
    dossier = engine.evaluate_quarantine_telemetry()

    assert "executive_quality_kpis" in dossier
    assert "annualized_avoided_scrap_teardown_usd" in dossier["executive_quality_kpis"]
    assert len(dossier["station_quarantine_breakdown"]) == 8


def test_timesfm_takt_forecaster():
    """Verify Google TimesFM-3 produces 60-minute forward takt time volatility forecasts."""
    forecaster = TimesFM3TaktForecaster()
    dossier = forecaster.generate_takt_forecast()

    assert "line_balancing_scorecard" in dossier
    trajectory = dossier["forecast_trajectory"]
    assert len(trajectory["timeline_minutes"]) == 90

    for i in range(len(trajectory["timeline_minutes"])):
        p10 = trajectory["forecast_lower_bound_p10_sec"][i]
        p50 = trajectory["forecast_cycle_time_p50_sec"][i]
        p90 = trajectory["forecast_upper_bound_p90_sec"][i]
        assert p10 <= p50 <= p90


def test_jis_logistics_synchronizer():
    """Verify 15-mile Plant Woodruff to Spartanburg JIS buffer and sequence parity."""
    synchronizer = BMWJISLogisticsSynchronizer()
    dossier = synchronizer.generate_jis_status()

    assert dossier["metadata"]["corridor_distance_miles"] == 15.0
    assert len(dossier["active_shuttle_convoys"]) == 3
    assert "jis_sequence_parity_rate" in dossier["jis_kpi_dashboard"]


def test_full_lakehouse_pipeline():
    """Verify end-to-end Medallion execution."""
    pipeline = BMWSpartanburgLakehousePipeline()
    result = pipeline.run_full_pipeline()

    assert result["pipeline_status"] == "SUCCESS"
    assert "avoided_teardown_savings_usd" in result
