# winter-supplement-engine
A rules engine for calculating BC Winter Supplement benefits.

---

## Contents

- [Assignment Goal](#assignment-overview)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)

## Assignment Goal

The goal of this assignment is to implement a business rules engine that determines eligibility and calculates the benefits a client is eligible to receive.

## Installation

Prerequisites:
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Python 3.8+](https://realpython.com/installing-python/)
- [Pipx](https://pipx.pypa.io/stable/installation/)

```bash
$ git clone https://www.github.com/mikesmvl/winter-supplement-engine.git
$ pipx install poetry
$ poetry install
$ cp .env.example .env
```

By default, the engine will run in wildcard subscription mode, processing **all requests** on `BRE/calculateWinterSupplementInput`. If you want to process requests for a specific MQTT topic ID:

Add the MQTT_TOPIC_ID in your .env file with the `MQTT Topic ID` displayed in the Winter Supplement Calculator. It should look something like:

```
MQTT_TOPIC_ID="8c882c0e-b4c3-41b4-9d71-a58e2df2f5cb"
```

## Usage

To start the business rules engine run

```shell
$ poetry run start
```

## Testing

To run the unit tests use
```shell
$ poetry run pytest
```
