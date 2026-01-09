# Website Traffic ETL with Apache Airflow

An ETL pipeline using Apache Airflow that analyzes website traffic data and sends daily email reports with the top 3 IP addresses by traffic volume.

## Quick Start (Docker + WSL)

### Prerequisites

- **Docker Desktop** with WSL 2 integration enabled
- **WSL** (Ubuntu recommended)

### 1. Clone and navigate to the repo

```bash
# In your WSL terminal (Ubuntu)
cd ~
git clone https://github.com/YOUR_USERNAME/website-traffic-etl-airflow.git
cd website-traffic-etl-airflow
```

### 2. Set your user ID (avoids permission issues)

```bash
# Check your user ID
id -u

# If it's not 1000, update .env:
echo "AIRFLOW_UID=$(id -u)" > .env
```

### 3. Start Airflow

```bash
docker compose up -d
```

Wait ~30 seconds for initialization, then check status:

```bash
docker compose ps
```

All services should show "healthy" or "running".

### 4. Access the Airflow UI

Open **http://localhost:8080** in your browser.

| | |
|---|---|
| **Username** | `airflow` |
| **Password** | `airflow` |

### 5. Run the DAG

1. Find `task_3` in the DAG list
2. Toggle it **ON** (top-left switch)
3. Click the **Play** button to trigger a manual run

### 6. Stop Airflow

```bash
docker compose down
```

To also remove the database (fresh start):

```bash
docker compose down -v
```

## Project Structure

```
website-traffic-etl-airflow/
├── dags/
│   └── task-3.py           # Main ETL DAG
├── data/
│   └── traffic_data.csv    # Sample traffic data (61K rows)
├── logs/                   # Airflow logs (auto-generated)
├── plugins/                # Custom Airflow plugins
├── docker-compose.yaml     # Docker services configuration
├── .env                    # Environment variables (AIRFLOW_UID)
└── README.md
```

## Where Things Live

| What | Location |
|------|----------|
| DAGs (your pipelines) | `./dags/` |
| Logs | `./logs/` |
| Input data | `./data/` |
| Airflow UI | http://localhost:8080 |

## The Pipeline

The `task_3` DAG runs daily at midnight and:

1. **Extracts** traffic data from CSV
2. **Transforms** by filtering low-traffic IPs and splitting AM/PM
3. **Loads** by sending email reports (requires SMTP config)

```
read_traffic_data → filter_ips → split_am_pm → filter_am → day_of_week → [do_nothing_am, send_email_am]
                                             → filter_pm → send_email_pm
```

## Configuration

### Email (Optional)

To enable email reports, add SMTP settings to `docker-compose.yaml` under `x-airflow-common.environment`:

```yaml
AIRFLOW__SMTP__SMTP_HOST: smtp.gmail.com
AIRFLOW__SMTP__SMTP_PORT: 587
AIRFLOW__SMTP__SMTP_STARTTLS: "true"
AIRFLOW__SMTP__SMTP_USER: your_email@gmail.com
AIRFLOW__SMTP__SMTP_PASSWORD: your_app_password
AIRFLOW__SMTP__SMTP_MAIL_FROM: your_email@gmail.com
```

Then update the recipient email in `dags/task-3.py` (search for `joegilldata@gmail.com`).

## Troubleshooting

### "Cannot connect to Docker daemon"

```bash
# If using Docker Desktop, make sure it's running
# If using Docker Engine in WSL:
sudo service docker start
```

### "Permission denied" on logs/

```bash
# Set correct ownership
sudo chown -R $(id -u):$(id -g) logs/
```

### DAG not appearing

```bash
# Check for syntax errors
docker compose exec airflow-webserver python /opt/airflow/dags/task-3.py

# Or check scheduler logs
docker compose logs airflow-scheduler
```

### Port 8080 already in use

Edit `docker-compose.yaml` and change the port mapping:

```yaml
ports:
  - "8081:8080"  # Access at localhost:8081
```

### Starting fresh

```bash
docker compose down -v
docker compose up -d
```

## Tech Stack

- **Airflow 2.7.0** - Workflow orchestration
- **PostgreSQL 15** - Metadata database
- **Python 3.11** - Runtime (inside container)
- **pandas/numpy** - Data processing

## Author

**Joseph Gill** - [joegilldata.com](https://joegilldata.com)
