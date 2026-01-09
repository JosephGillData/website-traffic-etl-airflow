# import packages

# standard packages
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from io import StringIO
import os

# airflow packages
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.utils.email import send_email
from airflow.operators.python_operator import BranchPythonOperator


# initiate a DAG instance
task_3 = DAG(
    "task_3",
    start_date=datetime(2023, 8, 19, 0, 0),
    schedule='0 0 * * *', # Run every day at midnight
    catchup=False,
    end_date=None,
)


# path configuration - works in both local and Docker environments
DATA_PATH = os.environ.get('AIRFLOW_HOME', '/opt/airflow') + '/data/traffic_data.csv'

# extract functions
def read_traffic_data(**kwargs):
    df_traffic_data = pd.read_csv(DATA_PATH) # load data from .csv
    # data cleaning and data processing
    df_traffic_data['bf_date'] = pd.to_datetime(df_traffic_data['bf_date'])
    df_traffic_data['bf_time'] = pd.to_datetime(df_traffic_data['bf_time'], format='%H:%M:%S').dt.time
    df_traffic_data['hour'] = df_traffic_data['bf_time'].apply(lambda x: x.hour)
    df_traffic_data['is_am'] = df_traffic_data['hour'] < 12
    kwargs['ti'].xcom_push(key='df_traffic_data', value=df_traffic_data) # this creates a variable that can be loaded downstream


# transform functions
def filter_ips(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='read_traffic_data', key='df_traffic_data') # load in the variable
    ip_traffic = df.groupby('ip')['gbps'].sum().reset_index() # aggregate the data by IP and calculate the total traffic   
    threshold = ip_traffic['gbps'].quantile(0.20) # determine the threshold for low-traffic IPs
    df_ips = ip_traffic[ip_traffic['gbps'] > threshold] # filter low-traffic IPs
    high_ips = df_ips['ip'].values.tolist()
    df_filtered = df[df['ip'].isin(high_ips)]
    kwargs['ti'].xcom_push(key='df_filtered', value=df_filtered)

split_am_pm = DummyOperator(task_id='split_am_pm', dag=task_3) # dummy operator so we can create AM and PM branches

def filter_am(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='filter_ips', key='df_filtered')
    df_am = df[df['is_am']] # create a dataset containing AM observations
    kwargs['ti'].xcom_push(key='df_am', value=df_am)

def filter_pm(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='filter_ips', key='df_filtered')
    df_pm = df[~df['is_am']] # create a dataset containing PM observations
    kwargs['ti'].xcom_push(key='df_pm', value=df_pm)


# load functions
def day_of_week(**kwargs):
    today = datetime.now()
    if today.weekday() < 5: # if it's a weekday, no nothing, if it's a weekend, send an email
        return "do_nothing_am"
    else:
        return "send_email_am"

def send_email_am(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='filter_am', key='df_am')
    today = datetime.now().date()
    ip_traffic = df.groupby('ip')['gbps'].sum().reset_index() # aggregate the data by IP and calculate the total traffic (sum of 'gbps')    
    ip_traffic_sorted = ip_traffic.sort_values(by='gbps', ascending=False) # sort the DataFrame in descending order by traffic ('gbps')
    top_ips = ip_traffic_sorted.values.tolist()
    # create the string that will be sent in the email
    top_ips_str = f"The Top three IP addresses with the most traffic before midday on {today} are {top_ips[0][0]}, {top_ips[1][0]} and {top_ips[2][0]}"
    # send the email
    send_email(
        to='joegilldata@gmail.com',
        subject='Top 3 Traffic IPs (AM Branch)',
        html_content=top_ips_str,
    )

def send_email_pm(**kwargs):
    ti = kwargs['ti']
    df = ti.xcom_pull(task_ids='filter_pm', key='df_pm')
    today = datetime.now().date()
    ip_traffic = df.groupby('ip')['gbps'].sum().reset_index() # aggregate the data by IP and calculate the total traffic (sum of 'gbps')    
    ip_traffic_sorted = ip_traffic.sort_values(by='gbps', ascending=False) # sort the DataFrame in descending order by traffic ('gbps')
    top_ips = ip_traffic_sorted.values.tolist()
    # create the string that will be sent in the email
    top_ips_str = f"The Top three IP addresses with the most traffic after midday on {today} are {top_ips[0][0]}, {top_ips[1][0]} and {top_ips[2][0]}"
    # send the email
    send_email(
        to='joegilldata@gmail.com',
        subject='Top 3 Traffic IPs (PM Branch)',
        html_content=top_ips_str,
    )


# convert functions to tasks

read_traffic_data = PythonOperator(
    task_id='read_traffic_data',
    python_callable=read_traffic_data,
    dag=task_3
)

filter_ips = PythonOperator(
    task_id='filter_ips',
    python_callable=filter_ips,
    dag=task_3
)

filter_am = PythonOperator(
    task_id='filter_am',
    python_callable=filter_am,
    dag=task_3
)

filter_pm = PythonOperator(
    task_id='filter_pm',
    python_callable=filter_pm,
    dag=task_3
)

day_of_week = BranchPythonOperator(
    task_id='day_of_week',
    python_callable=day_of_week,
    provide_context=True,
    dag=task_3,
)

send_email_am = BranchPythonOperator(
    task_id='send_email_am',
    python_callable=send_email_am,
    provide_context=True,
    dag=task_3,
)

do_nothing_am = DummyOperator(
    task_id='do_nothing_am',
    dag=task_3,
)

send_email_pm = BranchPythonOperator(
    task_id='send_email_pm',
    python_callable=send_email_pm,
    provide_context=True,
    dag=task_3,
)


# define dependencies
read_traffic_data >> filter_ips >> split_am_pm >> [filter_am, filter_pm]
filter_pm >> send_email_pm
filter_am >> day_of_week
day_of_week >> [do_nothing_am, send_email_am]

