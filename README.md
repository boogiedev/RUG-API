# RUG-API
Random User Generator(RUG) Statistics API

## Table of Contents

- [What is this?](#what-is-this?)
- [Approach](#approach)
  - [Steps](#Steps)
  - [Features](#features)
- [Usage](#usage)

---

## What is this?

Web service that has RESTful API endpoints for RUG data.

Scope of the data was interpreted to only include UTF-8 names and all locations within the US.

---

## Approach

### Steps

- [X] 1: Determine technologies/production stack needed for application
  - Flask, Gunicorn (WSGI), AWS Elastic Beanstalk, Pandas (Data Processing)
- [X] 2: Flesh out web service (figure out the endpoint(s))
  - Final endpoint - /get_statistics
  - Before requests, check if there is current (cleaned) data resource
    - Call /fill_data if not
  - Verify Stats & Data with /view_data and /view_statistics endpoint
- [X] 3: Build tests for all resources (header tests as well)
  - Build manual tests
    - Test for ACCEPT headers (user shouldnt have to specify format, automatically determined)
      - application/json
      - text/xml
      - text/plain
      - 406 Error for non compatible header
- [X] 4: Deploy (hopefully with CI/CD tools)
  - Elastic Beanstalk connected to repo


### Features

- Routes/Endpoints "/api/v0" {params}
  - [ ] fill_data {n_results} [GET] (Internal Endpoint, REFACTORED out of VIEW)
  - [ ] view_data [GET]
  - [ ] get_statistics {format} [GET]
  - [ ] view_statistics [GET]

---

## Usage

Show example usage
