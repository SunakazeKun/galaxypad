# galaxypad
![Custom Cosmic Spirit in Freezy Flake Galaxy](https://raw.githubusercontent.com/SunakazeKun/galaxypad/master/SCREENSHOT.png)

**galaxypad** is a Python command-line tool to record input playback files (PAD files) for [Tip Networks](https://www.mariowiki.com/Tip_Network) and [Cosmic Spirits](https://www.mariowiki.com/Cosmic_Spirit) in **Super Mario Galaxy 2**. The tool reads relevant information from [Dolphin Emulator](https://dolphin-emu.org/)'s emulated game memory and automatically produces a PAD file after recording stopped. The tool requires at least **Python 3.10**. It should also work with 3.11 and newer versions, but this hasn't been tested. Furthermore, it uses [py-dolphin-memory-engine](https://github.com/henriquegemignani/py-dolphin-memory-engine) to interact with Dolphin's game memory. In order to record player input during gameplay, [Syati](https://github.com/SunakazeKun/Syati)'s *PadRecord* code is required to supply the information from the game to this tool.

It is available on PyPI, meaning that you can easily install it with pip:
```
pip install galaxypad
```

# Limitations
There are gameplay-related aspects that Tip Networks and Cosmic Spirits don't account for. Keep these in mind when you want to record and play inputs!

- You should only record playback when playing as Mario. Both objects will be disabled when playing as Luigi.
- Both objects disable the Star Pointer completely. Thus, Mario can't interact with objects that require the Star Pointer, for example Pull Stars and Grapple Flowers.
- The game's pseudo-random number generator (PRNG) won't be reseeded to account for random events, such as enemies moving in random directions. Therefore, it can happen in some scenarios that the player gets damaged by enemies.

# Usage
In this section, it is assumed that the game you want to record player input in already uses Syati's *PadRecord* code. The general usage is this:
```
usage: galaxypad [-h] [-address [ADDRESS]] output_folder_path

Record PAD playback in SMG2 from Dolphin memory.

positional arguments:
  output_folder_path  folder to save PAD files to

options:
  -h, --help          show this help message and exit
  -address [ADDRESS]  address from which the tool retrieves PadRecordInfo*
```

The ``-address`` option is not required, as the tool assumes ``PadRecordInfo*`` is supplied at ``0x80003FFC`` by default.

# Recording
Before you can record playback, you need to add the following things in your galaxy first:

1. A player spawn point from which the recording should start. This spawn point should be used by Tip Networks and Cosmic Spirits too.
2. A ``PadRecordHelper`` object in the same zone as the previously added spawn point. Its Obj_arg0 has to be set to the  added spawn point's MarioNo value.

Now you are ready to use the tool:

1. Launch the modded game in Dolphin and start this command-line tool like explained in previous sections.
3. While the game is running, pay attention to the tool's console output to verify that everything is running correctly.
4. Once you are in the desired galaxy, go to where you placed PadRecordHelper. It doesn't use a model, but an A button icon will be displayed on the screen when you are close to it.
5. Once you press A, the scene will reset. After the scene has reloaded, the recording will start.
6. If you desire to stop recording, press 2 on the first player's Wiimote.

The tool keeps you informed about its current state, and it should inform you when something goes wrong. Here's an example from one of my tests:
```
Waiting for Dolphin...
Hooked to Dolphin, game ID is SB4P!
Searching for PadRecorderInfo* at 0x80003FFC...
Waiting for PadRecordHelper...
Started recording for spawn ID 0 in RedBlueExGalaxy!
Stopped recording!
Dumped 3075 KPAD frames (approx. 51 seconds) to '.\RedBlueExGalaxy\Dreamer0.pad'.
```

After recording, you can build a Ghost.arc containing the PAD file. However, this is beyond the scope of this tool. In final releases of your levels, you don't want players to interact with PadRecordHelper objects, so make sure to remove them once they are not needed anymore.