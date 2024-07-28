import argparse

from src.throttle.throttle import Throttle


def main():
    parser = argparse.ArgumentParser(
        description="Throttle: A progress loader for Python",
        epilog="Example usage:\n"
               "  python cli.py --loader bar --percentage 50\n"
               "  python cli.py --loader spinner --percentage 75",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--percentage',
        type=int,
        help='Progress percentage (0-100). This specifies how much of the task is completed.'
    )
    parser.add_argument(
        '--loader',
        type=str,
        choices=['spinner', 'bar', 'dots', 'time_clock'],
        help='Type of loader to display:\n'
             '  spinner    - A rotating spinner\n'
             '  bar        - A progress bar\n'
             '  dots       - Dots indicating progress\n'
             '  time_clock - A clock emoji indicating progress'
    )
    args = parser.parse_args()

    if args.loader and args.percentage is not None:
        total = 100
        completed = args.percentage

        loader = Throttle(total=total, style=args.loader)
        loader.completed = completed

        print(loader.render())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
