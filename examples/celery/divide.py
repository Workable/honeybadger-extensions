import argparse
import sys

from example_app.tasks import generic_div

def main():
    parser = argparse.ArgumentParser(description='Divide two integers')
    parser.add_argument('numerator', metavar='a', type=int, help='numerator')
    parser.add_argument('denominator', metavar='b', type=int, help='denominator')
    args = parser.parse_args()

    task = generic_div.delay(args.numerator, args.denominator)
    print('Start task %s' % task.id)

if __name__ == '__main__':
    main()
