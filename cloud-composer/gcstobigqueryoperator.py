import datetime
from airflow import models
from airflow.contrib.operators import gcs_to_bq
from airflow.contrib.operators.bigquery_operator import BigQueryOperator
DST_BUCKET_UTF8 = 'name_of_bucket/data'
yesterday = datetime.datetime.combine(
datetime.datetime.today() - datetime.timedelta(1),
datetime.datetime.min.time())
default_dag_args = {
'start_date': yesterday,
'email_on_failure': False,
'email_on_retry': False,
'retries': 1,
'retry_delay': datetime.timedelta(minutes=5),
# 'project_id': models.Variable.get('gcp_project')
}
with models.DAG(
'load_to_bigQuery',
schedule_interval='@daily',
default_args=default_dag_args) as dag:
    load_to_bq_from_gcs = gcs_to_bq.GoogleCloudStorageToBigQueryOperator(
    task_id='load_to_bq_from_gcs',
    source_objects='meteo.csv',
    write_disposition='overwrite',
    bucket=DST_BUCKET_UTF8,
    destination_project_dataset_table='utopios_data.meteo'
    )

    bq_query = BigQueryOperator(
        task_id='bq_query',
        sql="""SELECT * FROM utopios_data.meteo where type='TMIN' """,
        destination_dataset_table='utopios_data.meteo_min',
        create_disposition='CREATE_IF_NEEDED',
        bigquery_conn_id='bigquery_default'
    )

    load_to_bq_from_gcs >> bq_query
