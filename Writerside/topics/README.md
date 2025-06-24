![Rotting Research Logo](https://github.com/marshalmiller/rottingresearch/blob/a898614a4e933064a36478be259aee29b9f188fa/branding/project-banner/red/rottingresearch-github-project-banner-red.png)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Frottingresearch%2Frottingresearch.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Frottingresearch%2Frottingresearch?ref=badge_shield)

# Introduction

A project devoted to helping academics and researchers provide robust citations and mitigate link rot. Visit
[rottingresearch.org](https://rottingresearch.org/) to see it in action.


# Mission
Link rot is an established phenomenon that affects everyone who uses the internet. Researchers looking at individual subjects have recently addressed the extent of link rot’s influence on scholarly publications. One recent study found that 36% of all links in research articles were broken. 37% of DOIs, once seen as a tool to prevent link rot, were broken (Miller, 2022).

Rotting Research allows academics and researchers to upload their work and check the reliability of their citations. It extracts all of the links from the document and then checks to see if the link is accessible to the public.

Check out our website at [rottingresearch.org](https://rottingresearch.org/).

The status of our services can be observed at [status.rottingresearch.org/status/rr](https://status.rottingresearch.org/status/rr).

# Installation  
## Requirements
- Python3 (3.10+)
- Pip3
- Redis

## Docker Instructions  
### Local Development    
- Set the `APP_SECRET_KEY="RANDOM_SECRET_KEY"`  
- Run the docker container using `docker-compose up --build`. You can use the
`-d` flag to run the containers in 'detached' mode.  
- Open [127.0.0.1:8080](http://127.0.0.1:8080) in your browser.  

As docker volume is used, any changes made are reflected immediately. To view 
the container logs you can use `docker logs -f rottingresearch`. The `-f` flag 
is used for following the logs.

### Building Image  
- Build the docker image `docker build --tag rottingresearch .`
- Run image `docker run -d -p 8080:8080 rottingresearch`


## Linux/Mac  
- Clone Repository: `git clone https://github.com/rottingresearch/rottingresearch`  
- Change directory to `rottingresearch` - `cd rottingresearch`
- Run `source setup.sh` - the script will automatically install the packages 
and setup the environment variables

## Windows  
- Clone Repository: `git clone https://github.com/rottingresearch/rottingresearch`   
- Change directory to `rottingresearch` - `cd rottingresearch`  
- Install Python Packages: `pip3 install -r requirements.txt`  
- Edit `app.py` and set `app.config['UPLOAD_FOLDER']` to a valid temporary folder.  
- Set `APP_SECRET_KEY` environment variable - `setx APP_SECRET_KEY "random"`  
- Set `ENV` running environment variable `setx ENV "DEV"` 
- Run redis `redis-server`  
- Set REDIS_URL environment `setx REDIS_URL "redis://localhost:6379"`  
- Run app `python3 app.py`  
- Run Celery worker `celery -A app:celery_app worker -B`  
- Open [127.0.0.1:8080](http://127.0.0.1:8080) on your browser.  


# Code of Conduct  
For our code of conduct, please visit our [Code of Conduct page](https://github.com/rottingresearch/rottingresearch/blob/main/code_of_conduct.md).

# License  
This program is licensed with a [GPLv3 License](https://github.com/rottingresearch/rottingresearch/blob/main/LICENSE).


[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Frottingresearch%2Frottingresearch.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Frottingresearch%2Frottingresearch?ref=badge_large)