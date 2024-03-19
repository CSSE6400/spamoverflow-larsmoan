[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-7f7980b617ed060a017424585567c406b6ee15c891e84e1186181d67ecf80aa0.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=14280373)


STATUS:
Now the docker container manages to run the APP with working PostGres database.

docker compose up should do the trick


NOTE:
when running the tests using docker the following command should be used:
```
docker pull ghcr.io/csse6400/spamoverflow-functionality:latest
docker run --net='host' -e TEST_HOST='http://host.docker.internal:5000' ghcr.io/csse6400/spamoverflow-functionality:latest
```


TODO:
1. The get emails route is not even closed to finished. Need to open for query params and their corresponding logic
2. Manage to run the tests from the docker container for the spamoverflow-tests. Per now it runs, but no meaningful response as to what fails.