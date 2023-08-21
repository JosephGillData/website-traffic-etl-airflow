# `Sky Task 3`

### Introduction

This repository automates an ETL (extract, transform, load) solution using Apache Airflow in which an email is sent containing the top 3 IP addresses with the most amount of traffic in the AM and PM each day.

### Task

Use the traffic data provided in the attached traffic_data.csv file, to create an airflow DAG file to implement the following tasks. Airflow only runs once a day at midnight:
* Filter out 20% of ips (for example low traffic ips).
* Create a branch task for AM and PM traffic.
* Find top 3 traffic ips in the PM branch and send the results to the selected email address.
* Stop the process for the AM branch if the execution date is not weekend.
* Otherwise send the top 3 traffic ips to the same email above.

### Getting Started

1. Clone this repository.
2. Navigate to this folder in the terminal and crate a virtual environment - `python3 -m venv venv`.
3. Activate the virtual environment - `source venv/bin/activate`.
4. Install the required packages - `pip install -r requirements.txt`.
5. Create an airflow.cfg file with:
6. Initialse the databse - `airflow db init`.
7. Create a user -  `airflow users create --username USERNAME --firstname FIRSTNAME --lastname LASTNAME --password PASSWORD --role Admin --email EMAIL`.
8. Set the environment variables - `source .env`.
8. Run the airflow scheduler - `airflow scheduler`.
9. Create another terminal, activate the virtual environment, set environment variables and run airflow on a local port - `airflow webserver --port 8080`.

### The Dataset

The data is stored in `data/traffic_data.csv`. This dataset contains information on the network traffic of a site on the 13th August 2021. Each row represents a network data point or record. There are over 5 columns and over 60,000 rows. Here's an explanation of each column:
* **bf_date**: The date when the observation occurred.
* **bf_time**: The time when the observation occurred.
* **id**: A unique identifier for each observation.
* **ip**: The IP address associated with each observation.
* **gbps**: The traffic volume associated with each observation, measured in gigabits per second (Gbps). 

### ETL Process

The ETL process is performed by a directed acyclical graph (DAG) created in the `task-3` Python script. The image below shows the tasks that form the DAG and how they intereact via task dependencies.

![Alt Text](Dag.png)

#### Extract

* `read_traffic_data`: loads data from `traffic_data.csv` and creates a pandas dataset.

#### Tranform
* `filter_ips`: filters out 20% of the IP addresses with the lowest traffic.
* `split_am_pm`: creates a branch for the AM and PM data to be analysed in parallel.
* `filter_am`: filters the data to obtain observations created before midday.
* `filter_pm`: filters the data to obtain observations after before midday.

#### Load
* `day_of_week`: triggers the `do_nothing_am` function if it's a weekday and triggers the `send_email_am` if it's a weekend.
* `do_nothing_am`: does nothing.
* `send_email_am`: obtains the three IP addresses with the most traffic before midday and sends an email containing them.
* `send_email_pm`: obtains the three IP addresses with the most traffic after midday and sends an email containing them.

### Author 

Joseph Gill 

- [Visit My Personal Website](https://joegilldata.com)
- [LinkedIn Profile](https://www.linkedin.com/in/joseph-gill-726b52182/)
- [Twitter Profile](https://twitter.com/JoeGillData)
