# SpamOverflow

[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-7f7980b617ed060a017424585567c406b6ee15c891e84e1186181d67ecf80aa0.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=14280373)

## TODO:
- [ ] Detach the spamhammer from the post routine so that it doesn`t hold up any incomng requests. For now this is the main performance bottleneck.
- [ ] 

## Overview

SpamOverflow is a Flask-based API designed to handle incoming requests and process them efficiently. It includes functionalities such as spam detection using the SpamHammer library.

## Features

- Spam detection: Detects and filters out spam messages using the SpamHammer library.
- Efficient request handling: Designed for fast response times and scalability.

## Usage

### Locally

For local testing and development, use `docker-compose.yaml` and `Dockerfile.dev`:

```bash
docker-compose up
```

## Cloud deployment 
`Dockerfile.deploy` is used for cloud deployment and this is referenced in `main.tf` when building the docker image. 


```bash
terraform apply

cat api.txt
```


# TESTS:
```
docker run --rm --net='host' -e TEST_HOST='http://your-api-adress' spamoverflow-tests-local:latest
```