[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-7f7980b617ed060a017424585567c406b6ee15c891e84e1186181d67ecf80aa0.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=14280373)


STATUS:
Now the docker container manages to run the APP with working PostGres database.

docker compose up should do the trick


NOTE:
First time running the testsuite:

```
docker pull ghcr.io/csse6400/spamoverflow-functionality:latest
docker run --net='host' -e TEST_HOST='http://host.docker.internal:5000' ghcr.io/csse6400/spamoverflow-functionality:latest
```

After pulling it once you can simply run:
```
docker run --name spamoverflow_test_container --net='host' -e TEST_HOST='http://host.docker.internal:5000' -d ghcr.io/csse6400/spamoverflow-functionality

docker start spamoverflow_test_container

docker stop spamoverflow_test_container

```

TODO:
1. Detach the spamhammer from the post request and add it as a subroutine that can be triggered f.ex. By doing this we remove any lag on the server and can accept incoming request much faster.
