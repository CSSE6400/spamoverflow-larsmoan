#!/bin/bash

#Buildkit to make sure we know what env
export DOCKER_BUILDKIT=1

#Build the docker container
docker build -t s4827064 .

#Run the docker container in the background and remove after it is closed
docker run -d --rm -p 6400:6400 s4827064