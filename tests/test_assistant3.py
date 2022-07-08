"""Assistant3 Test."""

import queue
import argparse
import sounddevice as sd
from assistant3 import record, FeedbackIgnore, int_or_str

feedback_ignore_obj = FeedbackIgnore()
q: queue.Queue[bytes] = queue.Queue()
path = r'C:\Users\edwin\pythonprojekt\b\src\models\vosk-model-small-en-us-0.15'
print(path)

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
    record(args, path)
except KeyboardInterrupt:
    print('\nDone')
    parser.exit(0)

def test_text():
    try record(args, path)

