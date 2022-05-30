import datetime
import airflow

from airflow.operators import bash_operator

from airflow import models

bucket_id = models.Variable.get("bucket_id")


args = {}


# with airflow.DAG('exemple_dag',default_args=args, schedule_interval=datetime.timedelta(days=1)):
#     first_task = bash_operator.BashOperator(task_id='id_task', bash_command='echo hello > demo.txt && cat demo.txt')

first_dag = airflow.DAG('exemple_dag',default_args=args, schedule_interval=datetime.timedelta(days=1))
first_task = bash_operator.BashOperator(task_id='id_task', bash_command='echo hello > demo.txt && cat demo.txt', dag=first_dag)
second_task = bash_operator.BashOperator(task_id='id_task_2', bash_command='echo hello2 > demo2.txt && cat demo2.txt', dag=first_dag)

#airflow definition
first_task >> second_task