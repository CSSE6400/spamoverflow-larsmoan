[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-7f7980b617ed060a017424585567c406b6ee15c891e84e1186181d67ecf80aa0.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=14280373)


TODO:
1. Detach the spamhammer from the post request and add it as a subroutine that can be triggered f.ex. By doing this we remove any lag on the server and can accept incoming request much faster.


TODO - deployment to cloud:
1. Do I need autoscaling?
2. Get the .tf files from prac 4,5,6 and combine them to this repo.
3. Decide wether or not the main terraform file needs to build the docker image and then upload it to ECR, seems counterintuitive
4. Find out if we need a wait_for_db script such that prac 6 had or iw we can do it inline in the docker compose file as previosuly

4. Get an organized overview of all the ports etc. Maybe make a diagram 


5. "Remove" docker-compose as it is no longer needed for cloud hosting. Only if we want to run the postgres db locally.

    - because of this we will need the wait for db script