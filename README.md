# CodeBank

CodeBank is a collaborative performance system for live coding with FoxDot. It uses private and public working environments to encourage experimentation and improvisation in live performance. It is inspired by work by Fencott and Bryan-Kinns (2013) and Rohrhuber et al. (2007). It allows users to work on local versions of code before "pushing" their changes to a public server that generates audio for an audience. 

## Requirements

- [Python 3](https://www.python.org/downloads/)
- [FoxDot](https://github.com/Qirky/FoxDot)
- [SuperCollider](http://supercollider.github.io)
- One laptop for each user plus a machine, such as another laptop or Raspberry Pi, to run the server application

## Installation

- Download the zip from this repository and unpack in a directory you can access easily.
- Alternatively, build from source by cloning this repository:

```
git clone https://github.com/Qirky/CodeBank.git
cd CodeBank
python setup.py install
```

## Getting started

The first thing to do is make sure all the connecting computers are synchronised to the same time server. Doing so on a local network using something like [ptpd](https://github.com/ptpd/ptpd) will be more accurate but this can also be done over the internet. For example, Windows machines will usually synchronise to a server at `time.windows.com` or similar. Next, set up the server and connect to it using the client:

### Server

Open your command line interface (CLI), which will be Command Prompt on Windows or Terminal on Linux/Mac. Use the `cd` command to change to the directory CodeBank installed like so:

    cd path/to/CodeBank

Run the server by typing the following into the CLI


    python run-server.py

You will be prompted to set a password for the session, which will need to be entered by clients when they connect. Once you've set a password a display will appear on screen. 

### Client

Similar to the server, use the CLI to change directory to where CodeBank is installed. Start the client by running:

    python run-client.py

The graphical user interface (GUI) will open. Use the menu to go to "File" then "Connect to server". This will open a dialog where you can enter the IP address for the server (you can find this on the server display), a user name, and the password for the server. The textbox will be enabled and the user names for any  connected users will be displayed in the upper right of the GUI.

### Basics

Once connected, a user can type into the text box in bottom of the interface and press `Ctrl+Return` to evaluate code. This will only evaluate code locally on *that user's* computer. If you want to share your code will all connected users, use the `PUSH` button. This will add the code to the server and will be displayed in the large canvas in the GUI, called the Public Repository. The code is displayed with the colour associated with the user and can be accessed by any other user by clicking on it. These are called "codelets". Once a user clicks on a codelet, the background turns grey and cannot be accessed by other user's until the changes are pushed again. 

### Action buttons

#### PUSH

Send the code in textbox to the server, which will start playing it for the audience. If no codelet was selected, a new one is created. 

#### SOLO

Isolates the layer being worked on in the text box so you can hear it without the server audio.

#### RESET

Undoes any changes made to a codelet and unlocks it so it can be pulled by other users

#### ROLLBACK

Once a codelet is selected, this reverts it to its last state before it was last changed

#### HIDE

If a codelet is no longer needed, selecting it and pressing `HIDE` will remove  it from view in the public repository.

#### TOGGLE HIDDEN

Shows hidden codelets. Pulling a hidden codelet and pusing it will un-hide it.

#### CLEAR CLOCK

Clears the server's (and all users') scheduled events

## References

Fencott, Robin, and Nick Bryan-Kinns. 2013. “Computer Musicking: HCI, Cscw and Collaborative Digital Musical
Interaction.” In Music and Human-Computer Interaction, 189–205. Springer.

Rohrhuber, Julian, Alberto de Campo, Renate Wieser, Jan-Kees van Kampen, Echo Ho, and Hannes Hölzl. 2007. “Purloined
Letters and Distributed Persons.” In Music in the Global Village Conference (Budapest).