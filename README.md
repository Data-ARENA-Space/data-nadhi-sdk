# 🌊 Data Nadhi

**Data Nadhi** is an open-source platform that helps you manage the flow of data starting from your application logs all the way to your desired destinations — databases, APIs, or alerting systems.

> **Direct. Transform. Deliver.**  
> Flow your logs, trigger your pipelines.

---

## 🧠 What is Data Nadhi?

Data Nadhi provides a unified platform to **ingest, transform, and deliver** data — powered by **Temporal**, **MongoDB**, **Redis**, and **MinIO**.

It connects easily with your applications using the **Data Nadhi SDK**, and gives you full control over how data moves across your system.

### Core Concept
- **Direct** – Collect logs and data from your applications or external sources.  
- **Transform** – Use Temporal workflows to apply filters, enrichments, or custom transformations.  
- **Deliver** – Send the final processed data to any configured destination — all handled reliably and asynchronously.

Data Nadhi is designed to be **modular**, **developer-friendly**, and **ready for production**.

---

## 🏗️ System Overview

The platform is built from multiple services and tools working together:

| Component | Description |
|------------|-------------|
| [**data-nadhi-server**](https://github.com/Data-ARENA-Space/data-nadhi-server) | Handles incoming requests from the SDK and passes them to Temporal. |
| [**data-nadhi-internal-server**](https://github.com/Data-ARENA-Space/data-nadhi-internal-server) | Internal service for managing entities, pipelines, and configurations. |
| [**data-nadhi-temporal-worker**](https://github.com/Data-ARENA-Space/data-nadhi-temporal-worker) | Executes workflow logic and handles transformations and delivery. |
| [**data-nadhi-sdk**](https://github.com/Data-ARENA-Space/data-nadhi-sdk) | Python SDK for logging and sending data from applications. |
| [**data-nadhi-dev**](https://github.com/Data-ARENA-Space/data-nadhi-dev) | Local environment setup using Docker Compose for databases and Temporal. |
| [**data-nadhi-documentation**](https://github.com/Data-ARENA-Space/data-nadhi-documentation) | Documentation site built with Docusaurus (you’re here now). |

All components are connected through a shared Docker network, making local setup and development simple.

---

## ⚙️ Features

- 🧩 **Unified Pipeline** – Move data seamlessly from logs to destinations  
- ⚙️ **Custom Transformations** – Define your own transformations using Temporal  
- 🔄 **Reliable Delivery** – Retries, fault tolerance, and monitoring built in  
- 🧠 **Easy Integration** – Simple SDK-based setup for applications  
- 💡 **Developer Focused** – Dev containers and Docker-first setup for consistency  

---

## 📚 What's Inside this repository

This is the Python SDK for Data Nadhi that acts as a normal logger but also sends the request to the Server using the API when required

### Tech Stack
- **Python(logging)** - Framework used to create temporal worker
- **Docker** – For consistent local and production deployment 
- **Docker Network (`datanadhi-net`)** – Shared network for connecting all services locally  

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose  
- VS Code (with Dev Containers extension)

### Setup Instructions

> If you want to modify or test it, open it directly in a Dev Container.

**To use it as a package:**
1. Install it
    ```bash
    pip install git+https://github.com/Data-ARENA-Space/data-nadhi-sdk.git
    ```
2. Add the following to your `.env` file
    ```bash
    DATA_NADHI_API_KEY=<API-KEY>
    DATA_NADHI_SERVER_HOST=http://localhost
    ```
    - If your service runs inside the same Docker network, remove the `DATA_NADHI_SERVER_HOST` variable.
3. Add Log config file in `.datanadhi` folder - See [Log Config](/docs/architecture/sdk/log-config.md)
4. Try logging
    ```python
    from dotenv import load_dotenv
    from datanadhi import DataNadhiLogger
    load_dotenv()

    def main():
        # Set up API key (in production, use environment variable)
        # os.environ["DATA_NADHI_API_KEY"] = "dummy_api_key_123"

        # Initialize logger with module name
        logger = DataNadhiLogger(module_name="test_app")

        logger.info(
            "Testing basic stuff",
            context={
                "user": {
                    "id": "user123",
                    "status": "active",
                    "email_verified": True,
                    "type": "authenticated",
                    "permissions": {"guest_allowed": False},
                }
            },
        )
    ```

---

## 🔗 Links

- **Main Website**: [https://datanadhi.com](https://datanadhi.com)
- **Documentation**: [https://docs.datanadhi.com](https://docs.datanadhi.com)
- **GitHub Organization**: [Data-ARENA-Space](https://github.com/Data-ARENA-Space)

## 📄 License

This project is open source and available under the [GNU Affero General Public License v3.0](LICENSE).

## 💬 Community

- **GitHub Discussions**: [Coming soon]
- **Discord**: [Data Nadhi Community](https://discord.gg/gMwdfGfnby)
- **Issues**: [GitHub Issues](https://github.com/Data-ARENA-Space/data-nadhi-documentation/issues)
