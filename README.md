# RoboFarmer: An automated tool for a famous farming game.

## Overview

RoboFarmer is a python tool to automate the play of a certain farming related game. Currently it is in an early
research stage. Eventually it will work through a combination of screencapture (using opencv and the python win32 api)
and memory access (using the pure win32 api through ctypes) to automate some tedious tasks in
*Story of Seasons: Friends of Mineral Town*. Tentatively, this includes crop and livestock management.

## Requirements

There is a whole lot complicated OCR, image processing, and platform dependent memory tricks used in this application.
As such there are a few dependencies that need to be installed outside of this project. The python libraries are
detailed in requirements.txt and can be fulfilled with `pip install -r requirements.txt` (as always, I would *strongly*
recommend using a virtual environment). However, there are a few external dependencies that are also required.

Currently these are:

* Windows - the win32 API is used both for memory inspection and to take screenshots. Also, I'm pretty sure that the
game doesn't run on *nix or macos anyway.
* Google Tesseract - Currently used for OCR. I recommend [the UB-Manneheim Fork](https://github.com/UB-Mannheim/tesseract/wiki). 
The binary should be on your path variable.
* *Story of Seasons: Friends of Mineral Town* - I mean, you don't *need* it, but the program won't do anything for you
if you don't have it.

## Setup Instructions

As Robofarmer is in active (but possibly infrequent) development, it may be broken at any point in time. Requirements
and setup instructions are also subject to change. Setup currently involves cloning the repository and installing the
dependencies in requirements.txt.

## How to Use

You really can't at the moment, but you can run it and it will try to take continual screenshots of notepad currently.

## Motivation and Project Goals

I'm a big fan of the Story of Seasons games, and was very excited to see the remaster/port of *Friends of Mineral Town* on
Steam and PC. However, they're very time intensive games, and *Friends of Mineral Town* in particular is a game that I've
played through multiple times already. After about thirty hours of gameplay, usually there's still some goals I want to
achieve, but I start feeling fatigued by some of the daily tasks. So, I wanted to see if I could automate any of these
parts.

However, the larger motivation is much more research and skill oriented. I'm a security engineer by profession, and it's
very common for me to have to interface with complex applications in unusual ways. Several of the libraries, techniques,
and sub-goals of this project are areas that I want to practice or learn to apply to my professional work, especially in
a programmatic context.

### Why Python?

In some ways, Python is a silly language for this project. It makes heavy use of the win32 apis, and there's a memory
inspection component that will be awkward to handle using python. There are also concerns with speed down the line. 
There are some small benefits to using python here, especially once I start developing actual gameplay automation. It
also gives me access to open-cv, which will make image parsing and manipulation much easier.

The primary motivation here though is that python is a language that I use frequently for professional projects, so the
hope is to transfer any new skills or techniques I pick up here.

## Status

The tool can now examine the game and attempt to return the time. It's... okay at it. With a little bit of tuning though
we should be able to logic and reason around it.

## License

This work is made available under the MIT license. Please see the file 'LICENSE' in this distribution for license terms.