[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-7f7980b617ed060a017424585567c406b6ee15c891e84e1186181d67ecf80aa0.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=14280373)


TODO:
Late on when the application is said to scale and take into account high priority users we probably need a seperate process that actually does the scanning of the emails themselves.

I.e one process should simply save the scan-request and another should continously work on the database and actually do the scan requests themselves.
For now, this is done in the same process.

1. Extract the priority from the scan request via the email_id and save it in the database. 
2. 