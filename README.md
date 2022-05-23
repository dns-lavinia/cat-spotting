# cat-spotting

## Description

As the name of the project suggests, this application aims to detect cat faces, and collect some environmental data (only temperature and humidity at the moment) while a discord bot would send messages to a server (guild) with the gathered data.

## Setup

To install all of the needed modules to run the .py files, simply run `pip install -r requirements.txt` for every component of the
project (cat-spotting, discord-bot, firebase-api).

Besides the module requirements, an .env file is needed for every component that contains sensitive data, thus it is kept a secret.

## discord-bot

The discord bot has two background tasks, one that sends a message with general stats once a day, and another that sends a message every time a new entry is added in a firebase collection.

A message for the statistics sent once a day has the following structure:

```
[2022-05-20]
- Total 🐈 spotted: 5
- 🐈 spotted in the last 24 hours: 2
- Cat peak hours: [17, 12, 0]
```

## firebase-api

For the firebase connection, we chose to create a **firestore database** collection,
in which we would send data every time a cat is detected by the cat-spotting application.

The API contains a class named *Catbase* (cat + firebase), which has defined the needed methods to work with the firestore database from the cat-spotting application and the discord bot.

## cat-spotting

For the cat spotting application we used a raspberry pi zero board and connected an
arduino uno to it in order to have an easier way to read the environmental data
(temperature, humidity).

As for the cat face detection part, we used a
pre-trained Haar classifier from OpenCV, which can be downloaded from here:
https://github.com/opencv/opencv/tree/master/data/haarcascades.
