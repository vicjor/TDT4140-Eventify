# Eventify  
_By Victor Jørgensen, Sjur Wold, Eline Gotaas, Axel Kjønsberg, Katrine Nguyen and Ola Holte_

Eventify is a fictional service developed by Group 33 in the course TDT4140 Programvareutvikling at NTNU.
The group consists of six members, all 2nd year students at NTNU.



**You can find a short project description [here]()**  

  
### Motivation  
Our motivation for this project is to fulfill all requirements specified in our project description and from our product owner. 

### Build status
(Droppes om vi ikke får inn CI)
Denne forutsetter at CI er på plass. Skal være et slags "bilde" som viser om pipeline failer eller ikke. Droppes om vi ikke får på plass CI.  
![Build status](https://camo.githubusercontent.com/fa00b92302c0b97620b5a33bded99e3c09436479/68747470733a2f2f7472617669732d63692e6f72672f616b6173686e696d6172652f666f636f2e7376673f6272616e63683d6d6173746572)

### Code style    
PEP8-standard  
![Code style](https://camo.githubusercontent.com/d0f65430681b67b7104f6130ada8c098ec5f66ba/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f636f64652532307374796c652d7374616e646172642d627269676874677265656e2e7376673f7374796c653d666c6174)

### Screenshots
Screenshot of the home page of [Eventify](https://eventufypu.com)
![Imgur](https://i.imgur.com/5IF32S2.jpg)

For more visual documentation, visit [our user manual](https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-33/wikis/%23Vedlikeholdsplan/Brukermanual).

### Tech/framework used  
- Django
- Materialize
- Bootstrap

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

###Code Example

### How to use?
Check out our user manual at [link til brukermanual]

#### Online version  
Visit our website _https://eventifypu.com_
To make an account, press the "Register" button in the navbar.
See our gifs for how to join and create events, register credit cards and make connections with your friends.

#### Local version  
Some users might want to run our website on localhost. To do so, follow these instructions:
1. Clone our git repo in terminal  
   `$ git clone https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-33/`
2. Go to the directory gruppe-33 by typing   
`cd gruppe-33`
3. After successfully cloning, you need to install to install al the required packages.
To do this, navigate to /gruppe-33 and run the following  command in Terminal:  
    `$ pip install -r requirements.txt`
4. Create a virtual environment.  
    `$ virtualenv venv`
5. Activate the virtual environment by typing   
`$ . venv/bin/activate`. You should now see (venv) in your command line, indicating venv is active.
6. Run the following command  
    `python eventify/manage.py runserver`. 
7. Go to 127.0.0.1:8000 or localhost:8000 to browse our site
    
### Tests
@Axel!

#### Contribute
Want to contribute? Check out our [GitLab Page](https://gitlab.stud.idi.ntnu.no/programvareutvikling-v19/gruppe-33/wikis/%23Vedlikeholdsplan/Rutiner-for-evolusjon-og-endring)





