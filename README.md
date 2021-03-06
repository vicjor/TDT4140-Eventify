# Eventify  
_By Victor Jørgensen, Sjur Wold, Eline Gotaas, Axel Kjønsberg, Katrine Nguyen and Ola Holde_

Eventify is a fictional service developed by Group 33 in the course TDT4140 Programvareutvikling at NTNU.
The group consists of six members, all 2nd year students at NTNU.


**You can find a short project description [here](https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-33/wikis/%23Dokumentasjon/Prosjektbeskrivelse)**  


### Code style ![Code style](https://camo.githubusercontent.com/d0f65430681b67b7104f6130ada8c098ec5f66ba/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f636f64652532307374796c652d7374616e646172642d627269676874677265656e2e7376673f7374796c653d666c6174)
All logic is written in Python and we have followed PEP8-standard for all coding.

When it comes to documentation we tried writing code that is self documenting, i.e. that it is enough to read the code to understand what it does. In addition to this, we have also documented all functions in views.py-files.

### Screenshots and How to Use
Screenshot of the home page of [Eventify](https://eventifypu.com)
![Imgur](https://i.imgur.com/5IF32S2.jpg)

For more visual documentation, visit [our user manual](https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-33/wikis/%23Vedlikeholdsplan/Brukermanual).

### Technology and framework used  
- Django - Python Web framework
- Materialize - CSS framework
- Bootstrap - CSS framework 
- Digital Ocean - A Virtual Private Server (VPS) used to host our application on https://eventifypu.com

### Features  
The following is a list of features implemented on our webpage:
* [x] Register an account
* [x] Log in/out
* [x] Create events
* [x] Join events
* [x] Join waiting lists for events
* [x] Register credit cards to pay for tickets to events
* [x] Send contact requests to your friends
* [x] Invite your friends to private events
* [x] Email notifications when an event is deleted/updated, you receive and friend request/invitation and confirmation after joining an event.
* [x] See and clear your notifications in the navbar
* [x] Search for event-titles and events in your location

### Online version  
Visit our website [eventifypu.com](https://eventifypu.com)
To make an account, press the "Register" button in the navbar.
See our [gifs](https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-33/wikis/%23Vedlikeholdsplan/Brukermanual) for how to join and create events, register credit cards and make connections with your friends.

### Local version  
Some users might want to run our website on localhost. To run the project you need Python version 3.6 or newer, Git and pip installed. The following instructions assumes you are running Linux/MacOS. If you are a Windows user we recommend downloading [Git Bash](https://gitforwindows.org) to run the same commands.

##### Prerequisites 
If you already have Git, pip and Python installed, you can skip directly to 'Installation'

1. To install Python, type in your terminal
    `sudo apt-get install python3`
2. If you are on a macOS install Git by typing the following command. If you don't have Git installed, this will prompt you to install it.  
    `git --version`  
If your are on a Linux and on Fedora you can use the following command:  
 `sudo dnf install git-all`  
And if you are on a Linux and on Debian-based distribution use:  
 `sudo apt install git-all`  
3. Finally, install pip with this command
    `sudo easy_install pip`

That's it! Now you are all set for the installation of Eventify on your local machine.

#### Installation
Follow these steps to run Eventify local machine:
1. Clone our git repo in terminal  
```
git clone https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-33/
```
2. Go to the directory gruppe-33 by typing   
`cd gruppe-33`
3. After successfully cloning, you need to install all the required packages. Run the following command in Terminal:  
    `pip install -r requirements.txt`
4. Create a virtual environment.  
    `virtualenv venv`
5. Activate the virtual environment by typing   
    `. venv/bin/activate`  
You should now see (venv) in your command line, indicating venv is active.
6. Get the database up to date  
     `python eventify/manage.py migrate`
7. Run the following command  
    `python eventify/manage.py runserver`. 
8. Go to 127.0.0.1:8000 or localhost:8000 to browse our site

By entering "localhost:8000" you will land in a page with a default database. If you want admin authorization, you can use username: Victor and password: admin. 

    
### Tests
We are test-covering over 84% of our code as of today. These are mainly testing the back end functionality. The following badge shows current test-coverage, and is also displayed at the top of the front-page to our GitLab repo.

![coverage](https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-33/badges/master/coverage.svg)

If you want to run the tests you can use the following command in the terminal. Make sure you are inside the folder gruppe-33:  
    `python eventify/manage.py test`

If you want to test a specific module (or app) you just append the name of the module behind the above command. For a more detailed report concerning the test coverage, you should run:  
    `coverage run --source="." eventify/manage.py test`  
    `coverage report`

For an even more detailed report, where you can see which lines are tested and which are not, you type:  
    `coverage html`

A folder full with HTML files will then be generated. If you open the one called "index.html" in your default browser, you can select all the .py files in the project and see how the test coverage spread over the lines.  

### Hosting
To host our application we are using [Digital Ocean](https://digitalocean.com), a Virtual Private Server (VPS). All traffic goes through HTTPS using a free SSL certificate, [Let's Encrypt](https://letsencrypt.org).


**How the VPS runs our application**
- Server is running Ubuntu 18.04.2
- [Gunicorn](https://gunicorn.org/) (Python Web Server Gateway Interface (WSGI) HTTP server) is used to run the application
- [Nginx](https://www.nginx.com/) is used as a web server
- [Supervisord](http://supervisord.org/) is a process control system being run to restart the application if it crashes

After countless hours, we have not succeeded implementing Continous Delivery/Deployment, therefore deployment has to be done manually.
To deploy the latest version of the master branch we simply SSH into the server and pull the latest updates from Gitlab. This way we can deploy the latest version of Eventify to the end user within few minutes.

#### Contribute
Want to contribute? Check out our [GitLab Page for more information](https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-33/wikis/%23Vedlikeholdsplan/Rutiner-for-evolusjon-og-endring)