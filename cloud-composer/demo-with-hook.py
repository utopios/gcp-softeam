import datetime

from airflow import models
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.operators import python
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from google.cloud import bigquery
import logging


YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=1)
BUCKET_NAME = 'your-composer-bucket'
GCS_FILES = ['sql_query.txt']
PREFIX = 'data' # populate this if you stored your sql script in a directory in the bucket

default_args = {
    'owner': 'Composer Example',
    'depends_on_past': False,
    'email': [''],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    'start_date': YESTERDAY,
}

with models.DAG(
        'query_gcs_to_bq',
        catchup=False,
        default_args=default_args,
        schedule_interval='@daily') as dag:

    def read_gcs_file(**kwargs):
        hook = GCSHook()

        for gcs_file in GCS_FILES:

            #check if PREFIX is available and initialize the gcs file to be copied
            if PREFIX:
                object_name = f'{PREFIX}/{gcs_file}'

            else:
                object_name = f'{gcs_file}'

            #perform gcs hook download
            resp_byte = hook.download_as_byte_array(
                bucket_name = BUCKET_NAME,
                object_name = object_name,
            )

            resp_string = resp_byte.decode("utf-8")
            logging.info(resp_string)
            return resp_string

    read_gcs_op = python.PythonOperator(
            task_id='read_gcs',
            provide_context=True,
            python_callable=read_gcs_file,
            )

    sql_query = "{{ task_instance.xcom_pull(task_ids='read_gcs') }}" # store returned value from read_gcs_op

    def query_bq(sql):
        hook = BigQueryHook(bigquery_conn_id="bigquery_default", delegate_to=None, use_legacy_sql=False)
        client = bigquery.Client(project=hook._get_field("project"), credentials=hook._get_credentials())
        client.query(sql) # If you are not doing DML, you assign this to a variable and return the value

    execute_query = python.PythonOperator(
            task_id='query_bq',
            provide_context=True,
            python_callable=query_bq,
            op_kwargs = {
                "sql": sql_query
            }
            )

    read_gcs_op >> execute_query