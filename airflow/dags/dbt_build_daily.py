"""
airflow/dags/dbt_build_daily.py
Daily transformation, attribution modeling, testing, and documentation generation pipeline.

Executes:
  1. dbt source freshness (Observability gate)
  2. dbt build staging (Deduplication & normalization)
  3. dbt build intermediate (Margins & 4 attribution models)
  4. dbt build marts (Unit economics, channel performance, retention, leak analysis)
  5. dbt singular tests (Attribution credit conservation test)
  6. dbt docs generate (Lineage catalog)
"""

from datetime import datetime, timedelta
import os
import logging
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

AIRFLOW_HOME = os.getenv("AIRFLOW_HOME", "/opt/airflow")
DBT_DIR = os.getenv("DBT_PROJECT_DIR", os.path.join(AIRFLOW_HOME, "dbt_project"))

logger = logging.getLogger("airflow.task")


def notify_dbt_failure(context):
    """
    Alerting failure callback for transformation failures.
    """
    task_id = context.get("task_instance").task_id
    dag_id = context.get("task_instance").dag_id
    exec_date = context.get("execution_date")
    exception = context.get("exception")

    alert_msg = (
        f"🚨 [DBT PIPELINE ALERT] Modeling Failure!\n"
        f"• Task: {task_id}\n"
        f"• DAG: {dag_id}\n"
        f"• Execution Date: {exec_date}\n"
        f"• Exception: {exception}\n"
        f"Action: Please check dbt logs and failed test outputs."
    )
    logger.error(alert_msg)
    print(alert_msg)


default_args = {
    "owner": "analytics_engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=3),
    "execution_timeout": timedelta(minutes=60),
    "on_failure_callback": notify_dbt_failure,
}

with DAG(
    dag_id="dbt_build_daily",
    default_args=default_args,
    description="Daily execution of dbt transformation layers, attribution models, and data tests",
    schedule_interval="0 4 * * *",  # Daily at 04:00 UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["marketing", "dbt", "transformation", "attribution", "marts"],
    sla=timedelta(hours=1),
) as dag:

    # 1. Source Freshness check (soft-fail with warning in development)
    t_freshness = BashOperator(
        task_id="dbt_source_freshness",
        bash_command=f"cd {DBT_DIR} && dbt source freshness || echo '[WARNING] Source freshness check flagged historical landing data.'",
    )

    # 2. Staging Layer Build & Tests
    t_staging = BashOperator(
        task_id="dbt_staging_build",
        bash_command=f"cd {DBT_DIR} && dbt build --select staging",
    )

    # 3. Intermediate Layer Build & Tests
    t_intermediate = BashOperator(
        task_id="dbt_intermediate_build",
        bash_command=f"cd {DBT_DIR} && dbt build --select intermediate",
    )

    # 4. Marts Layer Build & Tests
    t_marts = BashOperator(
        task_id="dbt_marts_build",
        bash_command=f"cd {DBT_DIR} && dbt build --select marts",
    )

    # 5. Singular Attribution Credit Invariance Tests
    t_singular_tests = BashOperator(
        task_id="dbt_singular_tests",
        bash_command=f"cd {DBT_DIR} && dbt test --select test_type:singular",
    )

    # 6. Documentation & Lineage Generation
    t_docs = BashOperator(
        task_id="dbt_docs_generate",
        bash_command=f"cd {DBT_DIR} && dbt docs generate",
    )

    t_freshness >> t_staging >> t_intermediate >> t_marts >> t_singular_tests >> t_docs
