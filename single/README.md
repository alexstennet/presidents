# presidents

## Setup
If you are on Windows (don't worry, I am too), set up [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10) and proceed from there.

1. [Install Anaconda](https://conda.io/docs/user-guide/install/index.html) (available for Linux, Windows, and Mac).
2. Clone this repository in your preferred location by entering the following in a terminal:
~~~
git clone https://github.com/gitavi/presidents.git
~~~
3. Change directory to `presidents` by entering the following in a terminal:
~~~
cd presidents
~~~
4. Set up the appropriate environment by entering the following in a terminal:
~~~
make env
conda activate presidents
~~~
5. Change directory to `presidents/single` by entering the following in a terminal:
~~~
cd single
~~~

6. Start a round of Single Player Command Line presidents (where the AI is really dumb!) by entering the following into a terminal:
~~~
python spcl_presidents.py
~~~
7. Whenever you come back to play some more (hopefully often!), run the following in your local copy of the repository to update your game (note, this might actually prevent you from playing the game if the update breaks the game, but it won't be broken for long!):
~~~
git pull
~~~

**Please send suggestions and any behavior you think is a bug to senavi[at]berkeley[dot]edu.**

## How to Play presidents

## How to Play Single Player Command Line presidents

## Very High Level Plan

1. Design and implement a database for storing all data associated with games of presidents
2. Make in-browser presidents game which interfaces with database
3. Perform manual data analysis when desired and set up automatic analyses
4. Implement machine learning techniques to gain deeper statistical understanding
5. Create AI that learns presidents and plays against itself many times per day
6. Allow players to play against different levels of AI
7. Create mobile apps for presidents; price apps at $0; price analysis tools at $5 (all prices subject to change)