import datetime as dt
import os
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'ETL',
    'start_date': dt.datetime(2020, 5, 1),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}

dag = DAG(
    'airflow_etl_v01',
    catchup=False,
    default_args=default_args,
    description='ETL from Postgres to DynamoDB',
    schedule_interval='0 0 * * *',
)

task = BashOperator(
    task_id='etl_postgres2dynamodb',
    bash_command='python {}/etl_postgres2dynamodb.py {} {} {} {} --region {}'.format(   
        os.environ['ETL_HOME'],
        os.environ['ETL_FROM_TABLE'],
        os.environ['ETL_FROM_COLUMN'],
        os.environ['ETL_TO_TABLE'],
        os.environ['ETL_TO_KEY'],
        os.environ['ETL_REGION']
    ),
    dag=dag,
)

task
