# galaxypad
![Custom Cosmic Spirit in Freezy Flake Galaxy](https://raw.githubusercontent.com/SunakazeKun/galaxypad/master/SCREENSHOT.png)

**galaxypad** is a Python command-line tool to record input playback files (PAD files) for [Tip Networks](https://www.mariowiki.com/Tip_Network) and [Cosmic Spirits](https://www.mariowiki.com/Cosmic_Spirit) in **Super Mario Galaxy 2**. The tool reads relevant information from [Dolphin Emulator](https://dolphin-emu.org/)'s emulated game memory and automatically produces a PAD file after recording stopped. The tool requires at least **Python 3.10**. It should also work with 3.11 and newer versions, but this hasn't been tested. Furthermore, it uses [py-dolphin-memory-engine](https://github.com/henriquegemignani/py-dolphin-memory-engine) to interact with Dolphin's game memory. In order to record player input during gameplay, [Syati](https://github.com/SunakazeKun/Syati)'s *PadRecord* code is required to supply the information from the game to this tool.

It is available on PyPI, meaning that you can easily install it with pip:
```
pip install galaxypad
```

# Usage
In this section, it is assumed that the game you want to record player input in already uses Syati's *PadRecord* code. The general usage is this:
```
usage: galaxypad [-h] [-address [ADDRESS]] output_folder_path save_data_path save_data_index

Record PAD playback in SMG2 from Dolphin memory.

positional arguments:
  output_folder_path  folder to save PAD files to
  save_data_path      GameData.bin file to extract game data from
  save_data_index     player save slot index, starts at 1, usually ends at 3

options:
  -h, --help          show this help message and exit
  -address [ADDRESS]  address from which the tool retrieves PadRecordInfo*
```

The ``-address`` option is not required, as the tool assumes ``PadRecordInfo*`` is supplied at ``0x80003FFC`` by default.

By default, Dolphin Emulator saves Super Mario Galaxy 2 save files to ``C:/User/<YOURNAME>/Documents/Dolphin Emulator/Wii/title/00010000/<HEXID>/data/GameData.bin`` where ``<YOURNAME>`` is your username and ``<HEXID>`` is your game's ID. However, the ID depends on the version played:

| Version | Hexadecimal Game ID |
| ------- | ------------ |
| **SB4E** (Americas) | ``53423445`` |
| **SB4P** (Europe/Australia) | ``53423450`` |
| **SB4J** (Japan) | ``5342344a`` |
| **SB4K** (South Korea) | ``5342344b`` |
| **SB4W** (Taiwan/Hong Kong) | ``53423457`` |


Super Mario Galaxy 2 has three save slots with the following indexes.

| Index | Slot |
| ----- | ---- |
| 1 | Left |
| 2 | Center |
| 3 | Right |

# Recording
Before you can record playback, you need to add the following things in your galaxy first:

1. A player spawn point from which the recording should start. This spawn point should be used by Tip Networks and Cosmic Spirits too.
2. A ``PadRecordHelper`` object in the same zone as the previously added spawn point. Its Obj_arg0 has to be set to the  added spawn point's MarioNo value.

Now you are ready to use the tool:

1. Launch the modded game in Dolphin and start this command-line tool like explained in previous sections.
3. While the game is running, pay attention to the tool's console output to verify that everything is running correctly.
4. Once you are in the desired galaxy, go to where you placed PadRecordHelper. It doesn't use a model, but an A button icon will be displayed on the screen when you are close to it.
5. Once you press A, the scene will reset. After the scene reloaded, the recording will start.
6. If you desire to stop recording, press 2 on the first player's Wiimote.

The tool keeps you informed about its current state and it should inform you when something goes wrong. Here's an example from one of my tests:
```
Loading save data from 'D:\Dokumente\Dolphin Emulator\Wii\title\00010000\53423450\data\GameData.bin'...
Extracted game data for player #1!
Waiting for Dolphin...
Hooked to Dolphin, game ID is SB4P!
Searching for PadRecorderInfo* at 0x80003FFC...
Waiting for PadRecordHelper...
Started recording for spawn ID 2 in RedBlueExGalaxy!
Stopped recording!
Dumped 629 KPAD frames (approx. 10 seconds) to '.\RedBlueExGalaxy\Dreamer2.pad'.
```

After recording, you can build a Ghost.arc containing the PAD file. However, this is beyond the scope of this tool. In final releases of your levels, you don't want players to interact with PadRecordHelper objects, so make sure to remove them once they are not needed anymore.