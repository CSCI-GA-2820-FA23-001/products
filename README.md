# NYU DevOps Project Template
[![Build Status](https://github.com/CSCI-GA-2820-FA23-001/products/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA23-001/products/actions)
[![Build Status](https://github.com/CSCI-GA-2820-FA23-001/products/actions/workflows/bdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA23-001/products/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA23-001/products/graph/badge.svg?token=XFLEJRHXIJ)](https://codecov.io/gh/CSCI-GA-2820-FA23-001/products)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is a skeleton you can use to start your projects

## Overview

This project is **Products** microservices with Flask framework. Both unit and behave tests are included. You can use `flask run` start it, and the Swagger Docs support on `/apidocs`.


## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes


k8s/                - Kubernetes yaml
├── Dockerfile      - For building production image
└── ...             - APP Deployment, Postgres StatefulSet, Secret, Service, etc.

.tekton/            - OpenShift tekton yaml
├── pipeline.yaml   - CI & CD pipelines
├── tasks.yaml      - tasks in pipelines
└── workspace.yaml  - PVC for pipelines
└── events                  - event listener and trigger
    ├── event_listener.yaml 
    ├── route.yaml              - Listener and APP's routes
    └── trigger_binding.yaml
    └── trigger_template.yaml
```

## Database Structure

| Field Name | Type | Nullable | Remark |
| :---------- | :----------- | :-----------: |:----------- |
| id | *Integer* | No | |
| name | *String* | No | |
| description | *Text* | Yes | |
| price | *Float* | No | |
| available | *Boolean* | No | True or False |
| image_url | *Text* | Yes | |
| category | *Enum* | Yes | ELECTRONICS, PERSONAL_CARE, TOYS, SPORTS, FOOD, HEALTH, OTHERS |

## Product Service APIs

| Method | Example URI | Function | Description 
| ------ | ----------- | -------- | -------------
| GET    | `/api/products` | List     | Returns all the products in the databse (can be filtered by a query string)
| POST   | `/api/products` | Create   | Create a new product, and upon success, receive a Location header specifying the new order's URI
| POST   | `/api/products/collect` | Create   | Create multiple products, return these created
| PUT   | `/api/products/<product_id>` | Update   | Update fields of a existing product
| DELETE   | `/api/products/<product_id>` | Delete   | Delete a Product based on the id specified in the path
| GET   | `/api/products/<product_id>` | Read   | Read a Product based on the id specified in the path
| PUT   | `/api/products/<int:product_id>/change_availability` | Update   | change the availability of a Product based on the id

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
