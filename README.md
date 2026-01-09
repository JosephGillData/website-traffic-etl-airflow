# Website Traffic ETL with Apache Airflow

An automated ETL (Extract, Transform, Load) pipeline using Apache Airflow that analyzes website traffic data and sends daily email reports containing the top 3 IP addresses by traffic volume.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start (Docker - Recommended)](#quick-start-docker---recommended)
- [Manual Setup (Without Docker)](#manual-setup-without-docker)
- [WSL Setup (Windows Users)](#wsl-setup-windows-users)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [The Dataset](#the-dataset)
- [ETL Pipeline](#etl-pipeline)
- [Troubleshooting](#troubleshooting)
- [Author](#author)

## Overview

This pipeline performs the following tasks daily at midnight:

1. **Extract**: Loads traffic data from CSV
2. **Transform**:
   - Filters out the bottom 20% of IP addresses by traffic
   - Splits data into AM (before noon) and PM (after noon) branches
3. **Load**:
   - Sends PM traffic report via email (daily)
   - Sends AM traffic report via email (weekends only)

## Prerequisites

### For Docker Setup (Recommended)
- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

### For Manual Setup
- Python 3.8 - 3.11
- pip (Python package manager)

## Quick Start (Docker - Recommended)

The easiest way to run this project is using Docker Compose.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/website-traffic-etl-airflow.git
cd website-traffic-etl-airflow
```

### 2. Start the services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database
- Airflow Webserver (port 8080)
- Airflow Scheduler

### 3. Access the Airflow UI

Open your browser and go to: **http://localhost:8080**

Default credentials:
- Username: `airflow`
- Password: `airflow`

### 4. Enable the DAG

In the Airflow UI, find the `task_3` DAG and toggle it ON.

### 5. Stop the services

```bash
docker-compose down
```

To also remove the database volume:
```bash
docker-compose down -v
```

## Manual Setup (Without Docker)

### 1. Clone and navigate to the repository

```bash
git clone https://github.com/YOUR_USERNAME/website-traffic-etl-airflow.git
cd website-traffic-etl-airflow
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set the Airflow home directory

```bash
export AIRFLOW_HOME=$(pwd)
```

Or add to your `.bashrc`/`.zshrc`:
```bash
echo 'export AIRFLOW_HOME=/path/to/website-traffic-etl-airflow' >> ~/.bashrc
source ~/.bashrc
```

### 5. Create the Airflow configuration file

Create `airflow.cfg` in the project root:

```ini
[core]
load_examples = False
dags_folder = /path/to/website-traffic-etl-airflow/dags

[scheduler]
scheduler_heartbeat_sec = 10

[smtp]
smtp_host = smtp.office365.com
smtp_starttls = True
smtp_ssl = False
smtp_user = YOUR_EMAIL@outlook.com
smtp_password = YOUR_PASSWORD
smtp_port = 587
smtp_mail_from = YOUR_EMAIL@outlook.com
```

### 6. Initialize the database

```bash
airflow db init
```

### 7. Create an admin user

```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --password admin \
    --role Admin \
    --email admin@example.com
```

### 8. Start Airflow (requires two terminals)

**Terminal 1 - Start the scheduler:**
```bash
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

**Terminal 2 - Start the webserver:**
```bash
source venv/bin/activate
export AIRFLOW_HOME=$(pwd)
airflow webserver --port 8080
```

### 9. Access the UI

Open **http://localhost:8080** and log in with your credentials.

## WSL Setup (Windows Users)

If you're running this on Windows, use WSL (Windows Subsystem for Linux) for the best experience.

### Installing WSL

1. **Open PowerShell as Administrator** and run:
   ```powershell
   wsl --install
   ```

2. **Restart your computer** when prompted.

3. **Set up your Linux username and password** when WSL launches.

### Installing Docker on WSL

**Option A: Docker Desktop (Recommended for beginners)**

1. Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. In Docker Desktop settings, enable **"Use the WSL 2 based engine"**
3. Under **Resources > WSL Integration**, enable your WSL distribution

**Option B: Docker Engine directly in WSL (Ubuntu)**

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add the repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add your user to the docker group (to run without sudo)
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start
```

**Log out and back in** for group changes to take effect.

### Running the Project in WSL

1. **Open WSL terminal** (search "Ubuntu" or "WSL" in Windows Start menu)

2. **Navigate to your project:**
   ```bash
   cd /mnt/c/Users/YOUR_USERNAME/path/to/website-traffic-etl-airflow
   ```

   Or clone fresh into your WSL home directory (recommended for better performance):
   ```bash
   cd ~
   git clone https://github.com/YOUR_USERNAME/website-traffic-etl-airflow.git
   cd website-traffic-etl-airflow
   ```

3. **Start with Docker:**
   ```bash
   docker compose up -d
   ```

4. **Access the UI** at **http://localhost:8080**

### WSL Tips

- **Performance**: For better performance, keep your project files in the Linux filesystem (`~/projects/`) rather than `/mnt/c/`
- **VS Code Integration**: Install the [Remote - WSL extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl) to edit files seamlessly
- **Check Docker is running**: Run `docker ps` - if you get a permission error, ensure Docker service is started: `sudo service docker start`

## Configuration

### Email Configuration

To enable email notifications, configure SMTP settings:

**For Docker**: Create a `.env` file or modify `docker-compose.yaml` to add:
```yaml
environment:
  AIRFLOW__SMTP__SMTP_HOST: smtp.office365.com
  AIRFLOW__SMTP__SMTP_STARTTLS: "true"
  AIRFLOW__SMTP__SMTP_SSL: "false"
  AIRFLOW__SMTP__SMTP_USER: your_email@outlook.com
  AIRFLOW__SMTP__SMTP_PASSWORD: your_password
  AIRFLOW__SMTP__SMTP_PORT: 587
  AIRFLOW__SMTP__SMTP_MAIL_FROM: your_email@outlook.com
```

**For Manual Setup**: Edit `airflow.cfg` as shown in step 5 of the manual setup.

### Email Recipients

To change the email recipient, edit `dags/task-3.py` and update the `to` parameter in the `send_email_am` and `send_email_pm` functions.

## Project Structure

```
website-traffic-etl-airflow/
├── dags/
│   ├── task-3.py           # Main ETL DAG
│   └── data-vis.ipynb      # Data exploration notebook
├── data/
│   └── traffic_data.csv    # Traffic dataset (61,150 rows)
├── logs/                   # Airflow logs (auto-generated)
├── plugins/                # Custom Airflow plugins
├── docker-compose.yaml     # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── Dag.png                 # DAG visualization
└── README.md               # This file
```

## The Dataset

**Location**: `data/traffic_data.csv`

| Column    | Description                                    |
|-----------|------------------------------------------------|
| bf_date   | Date of the observation (YYYY-MM-DD)           |
| bf_time   | Time of the observation (HH:MM:SS)             |
| id        | Unique identifier for each observation         |
| ip        | IP address associated with the traffic         |
| gbps      | Traffic volume in gigabits per second          |

- **Rows**: 61,150
- **Date Range**: August 13-14, 2021

## ETL Pipeline

![DAG Visualization](Dag.png)

### Tasks

| Task              | Type              | Description                                           |
|-------------------|-------------------|-------------------------------------------------------|
| read_traffic_data | PythonOperator    | Loads CSV data into pandas DataFrame                  |
| filter_ips        | PythonOperator    | Removes bottom 20% of IPs by traffic                  |
| split_am_pm       | DummyOperator     | Branch point for parallel processing                  |
| filter_am         | PythonOperator    | Filters for morning observations (before noon)        |
| filter_pm         | PythonOperator    | Filters for afternoon observations (after noon)       |
| day_of_week       | BranchPythonOperator | Routes AM data based on weekday/weekend            |
| do_nothing_am     | DummyOperator     | No-op for weekday AM data                             |
| send_email_am     | PythonOperator    | Sends top 3 AM IPs (weekends only)                    |
| send_email_pm     | PythonOperator    | Sends top 3 PM IPs (daily)                            |

## Troubleshooting

### Docker Issues

**"Cannot connect to the Docker daemon"**
```bash
# Start Docker service
sudo service docker start

# Or if using Docker Desktop, ensure it's running
```

**"Port 8080 already in use"**
```bash
# Find what's using the port
sudo lsof -i :8080

# Or change the port in docker-compose.yaml:
ports:
  - "8081:8080"
```

**"Permission denied" errors**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Then log out and back in
```

### Airflow Issues

**DAG not appearing in UI**
- Check for Python syntax errors: `python dags/task-3.py`
- Ensure `AIRFLOW_HOME` is set correctly
- Wait a few minutes for the scheduler to pick it up

**Database errors**
```bash
# Reset the database (warning: loses all DAG history)
airflow db reset
airflow db init
```

**Import errors for pandas/numpy**
```bash
# Ensure you're in the virtual environment
source venv/bin/activate
pip install pandas numpy
```

### WSL Issues

**Slow file access on /mnt/c/**
- Move your project to the Linux filesystem: `~/projects/`
- Clone fresh instead of accessing Windows files

**Docker not working in WSL**
- Ensure Docker Desktop has WSL integration enabled
- Or start Docker service: `sudo service docker start`

## Future Improvements

- Deploy to cloud infrastructure (AWS, GCP, Azure)
- Connect to live data sources instead of static CSV
- Add HTML styling to email reports
- Implement data validation and error handling
- Add monitoring and alerting

## Author

**Joseph Gill**

- [Personal Website](https://joegilldata.com)
- [LinkedIn](https://www.linkedin.com/in/joseph-gill-726b52182/)
- [Twitter](https://twitter.com/JoeGillData)
