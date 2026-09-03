"""
BMW Plant Spartanburg Multi-Powertrain Assembly & AIQX Lakehouse
End-to-End Medallion Lakehouse Pipeline Orchestrator (src/processing/delta_lakehouse.py)
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ingestion.multi_station_stream_generator import SpartanburgMultiStationExtractor
from src.analytics.aiqx_defect_quarantine import BMWAIQXQuarantineEngine
from src.analytics.timesfm_takt_forecaster import TimesFM3TaktForecaster
from src.analytics.jis_logistics_optimizer import BMWJISLogisticsSynchronizer


class BMWSpartanburgLakehousePipeline:
    """Executes the complete Bronze -> Silver -> Gold Medallion Pipeline for BMW Plant Spartanburg."""

    def __init__(self):
        self.extractor = SpartanburgMultiStationExtractor()
        self.aiqx_engine = BMWAIQXQuarantineEngine()
        self.takt_forecaster = TimesFM3TaktForecaster()
        self.jis_synchronizer = BMWJISLogisticsSynchronizer()

    def run_full_pipeline(self) -> Dict[str, Any]:
        print("=" * 80)
        print("  STARTING BMW SPARTANBURG MULTI-POWERTRAIN MEDALLION LAKEHOUSE PIPELINE")
        print("=" * 80)

        # 1. Ingestion -> Bronze
        print("\n[STEP 1/4] Ingesting Multi-Station High-Frequency PLC & Sensor Telemetry...")
        raw_csv = self.extractor.generate_synthetic_telemetry(total_chassis=120)
        bronze_path = self.extractor.ingest_to_bronze(raw_csv)

        # 2. Bronze -> Silver
        print("\n[STEP 2/4] Cleansing & Partitioning Silver Line Performance Mart...")
        silver_path = self.extractor.build_silver_mart(bronze_path)

        # 3. Analytics -> Gold
        print("\n[STEP 3/4] Executing AIQX Defect Quarantine & JIS Logistics Optimization...")
        aiqx_dossier = self.aiqx_engine.evaluate_quarantine_telemetry()
        jis_dossier = self.jis_synchronizer.generate_jis_status()

        # 4. TimesFM-3 -> Gold
        print("\n[STEP 4/4] Executing Google TimesFM-3 Foundation Takt & Starvation Forecaster...")
        takt_dossier = self.takt_forecaster.generate_takt_forecast()

        result = {
            "pipeline_status": "SUCCESS",
            "target_facility": "BMW Group Plant Spartanburg (Hall 52)",
            "bronze_path": str(bronze_path),
            "silver_path": str(silver_path),
            "quarantined_early_incidents": aiqx_dossier["executive_quality_kpis"]["total_quarantined_at_early_stations"],
            "avoided_teardown_savings_usd": aiqx_dossier["executive_quality_kpis"]["annualized_avoided_scrap_teardown_usd"],
            "jis_parity_rate": jis_dossier["jis_kpi_dashboard"]["jis_sequence_parity_rate"],
            "takt_rebalance_lead_time": takt_dossier["line_balancing_scorecard"]["advance_rebalancing_lead_time"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat()
        }

        print("\n" + "=" * 80)
        print(f"  PIPELINE COMPLETE: {result['pipeline_status']}")
        print(f"  AIQX Early Quarantines: {result['quarantined_early_incidents']} | Scrap Savings: {result['avoided_teardown_savings_usd']}")
        print(f"  JIS Logistics Parity: {result['jis_parity_rate']} | Takt Lead Window: {result['takt_rebalance_lead_time']}")
        print("=" * 80)
        return result


if __name__ == "__main__":
    pipeline = BMWSpartanburgLakehousePipeline()
    pipeline.run_full_pipeline()
