import argparse
import sys

from . import pad


def handle_dolphin(args):
    output_folder_path: str = args.output_folder_path
    save_data_path: str = args.save_data_path
    save_data_index: int = args.save_data_index

    try:
        addr_pad_recorder_info_ptr: int = int(args.address, 0)
    except ValueError:
        print("Error! Address has an unknown number format!", file=sys.stderr)
        return

    print("Welcome to galaxypad! To find out how to set up the PAD recorder in a galaxy, please refer to the GitHub\n"
          "repository's README file! If you want to cancel the tool's execution, press CTRL+C any time. To stop\n"
          "recording, press 2 on the first player's Wiimote!\n"
          "------------------------------------------------------------------------------")
    try:
        pad.record_pad_from_dolphin(output_folder_path, save_data_path, save_data_index, addr_pad_recorder_info_ptr)
    except KeyboardInterrupt:
        print("Execution canceled.")


def main():
    parser = argparse.ArgumentParser(description="Record PAD playback in SMG2 from Dolphin memory.")

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    parser.add_argument("-address", nargs="?", default=f"0x{pad.ADDR_PAD_RECORDER_INFO_PTR:08X}", help="address from which the tool retrieves PadRecordInfo*")
    parser.add_argument("output_folder_path", help="folder to save PAD files to")
    parser.add_argument("save_data_path", help="GameData.bin file to extract game data from")
    parser.add_argument("save_data_index", type=int, help="player save slot index, starts at 1, usually ends at 3")
    parser.set_defaults(func=handle_dolphin)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
