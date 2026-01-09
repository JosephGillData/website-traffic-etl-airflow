from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def fail_task():
  raise ValueError("Intentional failure to test email alerts")

with DAG(
  dag_id="email_failure_test",
  start_date=datetime(2026, 1, 1),
  schedule_interval=None,
  catchup=False,
  default_args={
    "email": ["joegilldata@gmail.com"],
    "email_on_failure": True,
  },
) as dag:

  test_failure = PythonOperator(
    task_id="test_email_alert",
    python_callable=fail_task,
  )
