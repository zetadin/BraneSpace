# BraneSpace
## Currently:
An asteroids clone with wavelet meachanics instead of shooting.

## Eventually:
An extra-dimensional 2D space game written with pygame.
Single player, PVE, looter-shooter with tower defence elements.


To shorten interstellar trade routes, InterDimTrade Inc. egineers have found a way to travel through other parts of the multiverse, called branes.
The laws of physics in these branes are different, making the travel dangerous. So InterDimTrade has hired you to find or build safe trade routes through BraneSpace to a number of systems.

## To use:
The game is a python module with a __main__.py file that starts it. So to run the gme, run the module:
```
python -m BraneSpace
```

## Compiling the executables
BraneSpace uses [Nuitka](https://nuitka.net/) to build executables of the game that do not require Python to be installed.
To build them first create a virtual environment with all the dependencies, then run Nuitka.
For Linux, bash scripts are provided for these steps:
```
./setup_venv.sh
./build.sh
```

For Windows the only difference is activating the virtual environment requires a different command from the one in the Linux script:
```
.\BraneSpace_venv\Scripts\activate.bat
```

## Example Gameplay
![Gameplay](https://github.com/zetadin/BraneSpace/blob/main/screen_cap.webp?raw=true)
