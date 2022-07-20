"""CLI."""
import argparse

import sounddevice as sd

from .assistant3 import Assistant3, int_or_str
from assistant3 import processors


def main() -> None:
    """Assistant3 main function."""
    app = Assistant3()
    db_object = processors.make_db.MakeDB()

    print('-->')
    app.sdp.list_activation_docs()
    app.trigger.list_activation_docs()
    print('<--')
    app.plugin_watcher.list_plugins_by_uid()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        '-l',
        '--list-devices',
        action='store_true',
        help='show list of audio devices and exit',
    )
    args, remaining = parser.parse_known_args()
    if args.list_devices:
        print(sd.query_devices())
        parser.exit(0)
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[parser],
    )
    parser.add_argument(
        '-f',
        '--filename',
        type=str,
        metavar='FILENAME',
        help='audio file to store recording to',
    )
    parser.add_argument(
        '-d',
        '--device',
        type=int_or_str,
        help='input device (numeric ID or substring)',
    )
    args = parser.parse_args(remaining)

    try:
        app.record(args)
    except KeyboardInterrupt:
        print('\nDone')
        db_object.remove_db_plugin()
        parser.exit(0)


if __name__ == '__main__':
    main()
