Welcome to Nick's Bioinformatics sample! Brought to you by Nick Collins, Austin TX.

A few notes for building and running the docker image:

1) cd to directory that contains the Dockerfile (this dir)
2) Run `docker build -t challenge .` while in a terminal where docker is installed (for me, Docker Toolbox's quickstart
    terminal worked as a light linux VM on Windows)
3) Run `docker run -d -p 4000:80 challenge` (port 80 is exposed per the Dockerfile).
4) Go to `localhost:4000` if your OS matches the OS of the aforementioned terminal. If not, check the IP that the VM is
    running under, and replace 'localhost' with that when navigating to the website (typically 192.168.99.100)


A few notes for running integration tests:

Steps
1) Run the container for this project in detached mode:
    `docker run -d -p 4000:80 challenge`
2) Run the standalone-firefox container that Selenium has published in detached mode (specify port 4444):
    `docker run -d -p 4444:4444 selenium/standalone-firefox-debug`
3) Run `python tests.py`. Wait and see the results.

If that doesn't work (Connection Errors):
- check that docker is running on `localhost`. If it isn't, put the docker IP into the
    DOCKER_HOST setting (line 13, tests.py), and rerun `python tests.py`.
    - I was running Win OS with the Docker Toolbox Linux VM, the IP was '192.168.99.100' by default.

Another thing worth trying if you're having trouble:
Set 0.0.0.0:4444 as the remote end point, and <dockerhost LAN ip>:4000 as the URL for the application.

If you're still having trouble, feel free to contact me (kynickcollins@gmail.com) and we'll figure it out.
