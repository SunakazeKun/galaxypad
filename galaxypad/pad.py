from __future__ import annotations
from io import BytesIO

import sys
import time
import os.path
import struct
import dolphin_memory_engine

__all__ = ["write_pad_header", "write_game_data", "write_packet_header", "compress_kpad_states", "align_stream_32"]


def validate_ptr(name: str):
    def inner(func):
        def wrapper(*args, **kwargs):
            if args[0] == 0:
                raise IndexError(f"{name} is NULL!")
            return func(*args, **kwargs)
        return wrapper
    return inner


UNINITIALIZED_GAME_ID = "\0\0\0\0"
VALID_GAME_IDS = ["SB4P", "SB4E", "SB4J", "SB4K", "SB4W"]


# ----------------------------------------------------------------------------------------------------------------------
# PadRecorderInfo accessors for Dolphin
# The following values should be in sync with the respective information contained within "PadRecord.h"!

RECORDER_MODE_WAITING = 0
RECORDER_MODE_PREPARING = 1
RECORDER_MODE_RECORDING = 2
RECORDER_MODE_STOPPED = 3

ADDR_PAD_RECORDER_INFO_PTR = 0x80003FFC
OFFSET_UPDATE_FRAME = 0x00
OFFSET_READ_DATA_INFO = 0x04
OFFSET_RECORDER_MODE = 0x08
OFFSET_STAGE_NAME_PTR = 0x0C
OFFSET_RESTART_ID = 0x10
OFFSET_RESTART_ZONE_ID = 0x14
OFFSET_BACKUP_GAME_DATA_PTR = 0x18
OFFSET_BACKUP_GAME_DATA_SIZE = 0x1C


def dolphin_get_game_id() -> str:
    """
    Reads and returns the game's ID name from Dolphin's emulated game memory.

    :return: the game's ID name.
    """
    return dolphin_memory_engine.read_bytes(0, 4).decode("ascii")


@validate_ptr("s32*")
def dolphin_read_s32(ptr: int) -> int:
    """
    Reads a signed 32-bit integer at the specified address in Dolphin's emulated game memory and returns it.

    :param ptr: the pointer to the signed 32-bit integer.
    :return: the value read.
    """
    return dolphin_memory_engine.read_word(ptr)


@validate_ptr("u32*")
def dolphin_read_u32(ptr: int) -> int:
    """
    Reads an unsigned 32-bit integer at the specified address in Dolphin's emulated game memory and returns it.

    :param ptr: the pointer to the unsigned 32-bit integer.
    :return: the value read.
    """
    return dolphin_memory_engine.read_word(ptr) & 0xFFFFFFFF


@validate_ptr("char*")
def dolphin_read_cstring(ptr: int, encoding: str = "ascii") -> str:
    """
    Reads a C-string at the specified address in Dolphin's emulated game memory and returns it.

    :param ptr: the pointer to the C-string.
    :param encoding: the string's encoding.
    :return: the value read.
    """
    chars = bytearray()
    while True:
        char = dolphin_memory_engine.read_byte(ptr)
        ptr += 1
        if char == 0:
            break
        else:
            chars.append(char)
    return chars.decode(encoding)


@validate_ptr("PadRecorderInfo*")
def dolphin_read_update_frame(pad_recorder_info_ptr: int) -> int:
    """
    Reads the update frame number associated with the PadRecordInfo in Dolphin's emulated game memory and returns it.

    :param pad_recorder_info_ptr: the pointer to PadRecordInfo.
    :return: the value read.
    """
    return dolphin_read_u32(pad_recorder_info_ptr + OFFSET_UPDATE_FRAME)


@validate_ptr("PadRecorderInfo*")
def dolphin_read_recorder_mode(pad_recorder_info_ptr: int) -> int:
    """
    Reads the recorder mode associated with the PadRecordInfo in Dolphin's emulated game memory and returns it.

    :param pad_recorder_info_ptr: the pointer to PadRecordInfo.
    :return: the value read.
    """
    return dolphin_read_s32(pad_recorder_info_ptr + OFFSET_RECORDER_MODE)


@validate_ptr("PadRecorderInfo*")
def dolphin_read_stage_name(pad_recorder_info_ptr: int) -> str | None:
    """
    Reads the stage's name associated with the PadRecordInfo in Dolphin's emulated game memory and returns it.

    :param pad_recorder_info_ptr: the pointer to PadRecordInfo.
    :return: the value read.
    """
    stage_name_ptr = dolphin_read_u32(pad_recorder_info_ptr + OFFSET_STAGE_NAME_PTR)
    return dolphin_read_cstring(stage_name_ptr)


@validate_ptr("PadRecorderInfo*")
def dolphin_read_restart_id(pad_recorder_info_ptr: int) -> int:
    """
    Reads the spawn ID associated with the PadRecordInfo in Dolphin's emulated game memory and returns it.

    :param pad_recorder_info_ptr: the pointer to PadRecordInfo.
    :return: the value read.
    """
    return dolphin_read_s32(pad_recorder_info_ptr + OFFSET_RESTART_ID)


@validate_ptr("PadRecorderInfo*")
def dolphin_read_kpad_statuses(pad_recorder_info_ptr: int) -> list[bytes]:
    """
    Reads the KPADStatus structs associated with the PadRecordInfo in Dolphin's emulated game memory and returns them.

    :param pad_recorder_info_ptr: the pointer to PadRecordInfo.
    :return: the value read.
    """
    wpad_read_data_info_ptr = dolphin_read_u32(pad_recorder_info_ptr + OFFSET_READ_DATA_INFO)
    status_ptr = dolphin_read_u32(wpad_read_data_info_ptr + 0)
    status_count = dolphin_read_u32(wpad_read_data_info_ptr + 4)

    statuses = []

    for _ in range(status_count):
        status = dolphin_memory_engine.read_bytes(status_ptr, 0xF0)
        statuses.append(status)
        status_ptr += 0xF0

    return statuses


@validate_ptr("PadRecorderInfo*")
def dolphin_read_backup_game_data(pad_recorder_info_ptr: int) -> bytes:
    """
    Reads the GameData backup associated with the PadRecordInfo in Dolphin's emulated game memory and returns it.

    :param pad_recorder_info_ptr: the pointer to PadRecordInfo.
    :return: the GameData backup read.
    """
    backup_ptr = dolphin_read_u32(pad_recorder_info_ptr + OFFSET_BACKUP_GAME_DATA_PTR)
    backup_size = dolphin_read_u32(pad_recorder_info_ptr + OFFSET_BACKUP_GAME_DATA_SIZE)

    return dolphin_memory_engine.read_bytes(backup_ptr, backup_size)


# ----------------------------------------------------------------------------------------------------------------------
# PAD writer helpers

def write_pad_header(stream):
    """
    Writes a PAD format header to the specified stream.

    :param stream: the stream to write to.
    """
    stream.write(struct.pack(">I60x", 64))


def write_game_data(stream, game_data: bytes | bytearray):
    """
    Writes buffered game data to the specified stream.

    :param stream: the stream to write to.
    :param game_data: the buffered game data.
    """
    stream.write(struct.pack(">I", len(game_data)))
    stream.write(game_data)


def write_packet_header(stream, packet_index: int, packet_size: int, packet_states: int):
    """
    Writes a packet header containing the frame information to the specified stream.

    :param stream: the stream to write to.
    :param packet_index: the packet's index.
    :param packet_size: the size of compressed KPAD statuses.
    :param packet_states: the number of KPAD statuses.
    """
    packet_header = packet_index & 0xFF
    packet_header |= (packet_size & 0xFFFF) << 8
    packet_header |= (packet_states & 0xFF) << 24
    stream.write(struct.pack(">I", packet_header))


def compress_kpad_states(kpad_states: list[bytes], previous_kpad_state: bytearray) -> bytes:
    """
    Compresses a frame's KPADStatus structs and returns the compressed ``bytes`` object.

    :param kpad_states: the frame's KPADStatus structs to be compressed.
    :param previous_kpad_state: the previous KPADStatus.
    :return: the compressed KPADStatus bytes.
    """
    out = BytesIO()

    for state in kpad_states:
        blocks = bytearray(33)
        chunks = bytearray()

        for i, chunk in enumerate(state):
            if chunk != previous_kpad_state[i]:
                previous_kpad_state[i] = chunk
                chunks.append(chunk)

                blocks[i // 8] |= (1 << (i % 8))

        out.write(blocks)
        out.write(chunks)

    return out.getbuffer().tobytes()


def align_stream_32(stream):
    """
    If the specified stream is not aligned to 32 bytes, the necessary number of zero bytes needed for alignment will be
    written to the stream.

    :param stream: the stream to write to.
    """
    padding_size = ((stream.tell() + 31) & ~31) - stream.tell()
    stream.write(bytes(padding_size))


# ----------------------------------------------------------------------------------------------------------------------
# GameData helpers

def truncate_game_data(game_data: bytes) -> bytes:
    src = BytesIO(game_data)
    game_data_header = src.read(4)
    sections_count = game_data_header[0x1]

    dest = BytesIO()
    dest.write(game_data_header)

    for _ in range(sections_count):
        section_header = src.read(12)
        section_data_length = struct.unpack_from(">I", section_header, 0x8)[0] - 12
        section_data = src.read(section_data_length)

        dest.write(section_header)
        dest.write(section_data)

    return dest.getbuffer().tobytes()


# ----------------------------------------------------------------------------------------------------------------------
# Main functionality

def record_pad_from_dolphin(output_folder_path: str, addr_pad_recorder_info_ptr: int = ADDR_PAD_RECORDER_INFO_PTR):
    pad_recorder_info_ptr = 0
    recorder_state = RECORDER_MODE_WAITING
    game_id = UNINITIALIZED_GAME_ID

    if os.path.exists(output_folder_path) and not os.path.isdir(output_folder_path):
        print(f"Error! Path '{output_folder_path}' is not a folder!", file=sys.stderr)

    # 2 - Hook to Dolphin and check if game ID is supported
    print("Waiting for Dolphin...")

    while not dolphin_memory_engine.is_hooked():
        sleep_millis(500)
        dolphin_memory_engine.hook()

    while game_id == UNINITIALIZED_GAME_ID:
        sleep_millis(500)
        game_id = dolphin_get_game_id()

    print(f"Hooked to Dolphin, game ID is {game_id}!")

    if game_id not in VALID_GAME_IDS:
        print("WARNING! Detected game's ID does not appear to be SMG2, tool may fail!")

    # 3 - Find PadRecorderInfo and wait for recording
    print(f"Searching for PadRecorderInfo* at 0x{addr_pad_recorder_info_ptr:08X}...")

    while pad_recorder_info_ptr == 0:
        sleep_millis(250)
        pad_recorder_info_ptr = dolphin_read_u32(addr_pad_recorder_info_ptr)

    print("Waiting for PadRecordHelper...")

    while recorder_state == RECORDER_MODE_WAITING:
        sleep_millis(50)
        recorder_state = dolphin_read_recorder_mode(pad_recorder_info_ptr)

    if recorder_state == RECORDER_MODE_STOPPED:
        print("Aborted recording! Wait for scene to reset, then start again!")
        dolphin_memory_engine.un_hook()
        return

    game_data = dolphin_read_backup_game_data(pad_recorder_info_ptr)
    game_data = truncate_game_data(game_data)

    while recorder_state == RECORDER_MODE_PREPARING:
        recorder_state = dolphin_read_recorder_mode(pad_recorder_info_ptr)

    # 5 - Get general information and prepare output
    stage_name = dolphin_read_stage_name(pad_recorder_info_ptr)
    restart_id = dolphin_read_restart_id(pad_recorder_info_ptr)
    total_frames = 0

    print(f"Started recording for spawn ID {restart_id} in {stage_name}!")

    pad_folder_path = os.path.join(output_folder_path, stage_name)
    pad_file_path = os.path.join(pad_folder_path, f"Dreamer{restart_id}.pad")
    os.makedirs(pad_folder_path, exist_ok=True)

    with open(pad_file_path, "wb") as f:
        write_pad_header(f)
        write_game_data(f, game_data)

        current_packet_index = 0
        previous_state = bytearray(240)

        current_frame = dolphin_read_update_frame(pad_recorder_info_ptr)
        next_frame = (current_frame + 1) & 0xFFFFFFFF

        while recorder_state == RECORDER_MODE_RECORDING:
            # Get current update frame
            current_frame = dolphin_read_update_frame(pad_recorder_info_ptr)

            if current_frame == ((next_frame - 1) & 0xFFFFFFFF):
                continue
            elif current_frame != next_frame:
                print("Aborted recording due to a synchronization error!")
                dolphin_memory_engine.un_hook()
                return

            next_frame = (current_frame + 1) & 0xFFFFFFFF

            # Still recording?
            recorder_state = dolphin_read_recorder_mode(pad_recorder_info_ptr)

            if recorder_state != RECORDER_MODE_RECORDING:
                break

            # Dump KPADStatus structs from memory
            status_dumps = dolphin_read_kpad_statuses(pad_recorder_info_ptr)
            status_count = len(status_dumps)
            total_frames += 1

            # Compress statuses and create packet for player 1 input
            compressed_packet = compress_kpad_states(status_dumps, previous_state)
            write_packet_header(f, current_packet_index, len(compressed_packet), status_count)
            f.write(compressed_packet)
            current_packet_index += 1

            # Dummy packet for player 2 input
            write_packet_header(f, current_packet_index, 0, 0)
            current_packet_index += 1

        # Write eof header and align storage
        write_packet_header(f, current_packet_index + 192, 0, 0)
        align_stream_32(f)

        print("Stopped recording!")

    dolphin_memory_engine.un_hook()

    print(f"Dumped {total_frames} KPAD frames (approx. {total_frames // 60} seconds) to '{pad_file_path}'.")


def sleep_millis(millis: int):
    time.sleep(millis / 1000)
