import logging
from airflow.models import BaseOperator
import logging
class CustomOperator(BaseOperator):

    def __init__(self, *args, **kwargs):
        super(CustomerOperator,self).__init__(*args, **kwargs)
    def execute(self, context):
        # start Execution of operator
        logging.info("Start operatorExecution")