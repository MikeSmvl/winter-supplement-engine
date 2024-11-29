# Winter Supplement Engine
A rules engine for calculating BC Winter Supplement benefits.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
  - [Docker Setup](#docker-setup)
  - [Poetry Setup](#poetry-setup)
- [Usage](#usage)
  - [Running with Docker](#running-with-docker)
  - [Running with Poetry](#running-with-poetry)
- [Testing](#testing)
  - [Testing with Docker](#testing-with-docker)
  - [Testing with Poetry](#testing-with-poetry)

## Overview

The goal of this assignment is to implement a business rules engine that determines eligibility and calculates the benefits a client is eligible to receive.

## Installation

Prerequisites:
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

Clone the repository
```bash
git clone https://www.github.com/mikesmvl/winter-supplement-engine.git
cd winter-supplement-engine/
```

Copy the example env file
```bash
cp .env.example .env
```

Continue with the installation by either following the `Docker Setup` or the `Poetry Setup`.

#### Docker Setup
Prerequisites:
- [Docker](https://www.docker.com/get-started/) (installed/running)

Build the Docker Image
```
docker build -t winter-supplement-engine .
```

#### Poetry Setup
- [Python 3.8+](https://realpython.com/installing-python/)
- [Pipx](https://pipx.pypa.io/stable/installation/)

Install poetry using pipx
```bash
pipx install poetry
poetry install
```


## Usage

The engine processes requests by default in wildcard subscription mode, handling **all requests** on the `BRE/calculateWinterSupplementInput` topic.

### Custom Configuration
To process requests for a specific MQTT topic, update your `.env` file with the `MQTT_TOPIC_ID` given by the Winter Supplement Calculator:
```plaintext
MQTT_TOPIC_ID="8c882c0e-b4c3-41b4-9d71-a58e2df2f5cb"
```

### Running with Docker
Start the engine using Docker:
```bash
docker run --rm --env-file .env winter-supplement-engine
```

### Running with Poetry
Start the engine using Poetry:
```bash
poetry run start
```

## Testing

### Testing with Docker
To run the unit tests with Docker use:
```bash
docker run --rm --entrypoint poetry winter-supplement-engine run pytest
```

### Testing with Poetry
To run the unit tests with Poetry use:
```bash
poetry run pytest
```
