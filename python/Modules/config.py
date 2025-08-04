# config.py
import argparse
from datetime import datetime


def parse_args():
    """
    Parse command-line arguments and return a configuration object.
    """
    parser = argparse.ArgumentParser(
        description="Experiment configuration for EBDMTask"
    )
    parser.add_argument('-s', '--subject-id', type=str, required=True,
                        help='Participant identifier (e.g., S01)')
    parser.add_argument('-l', '--language', type=str, default='en',
                        choices=['en', 'fr'],
                        help='Experiment language')
    parser.add_argument('-t', '--stimulation', type=str, default='none',
                        help='Type of stimulation (e.g., none, tms)')
    parser.add_argument('-p', '--population', type=str, default='control',
                        help='Population group (e.g., control, patient)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode (console logs, faster timings)')
    parser.add_argument('--eyetracker', action='store_true',
                        help='Enable eye-tracking data collection')
    parser.add_argument('--test-dev', action='store_true',
                        help='Enable test/dev mode (mock inputs and WS)')
    args = parser.parse_args()

    # Generate timestamp for session (YYYYMMDD_HHMMSS)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    args.timestamp = timestamp

    # Define output filename prefix
    args.output_prefix = f"{args.subject_id}_{timestamp}"

    return args


if __name__ == '__main__':
    cfg = parse_args()
    print(f"Loaded configuration: {cfg}")