import argparse
import re
import sys
import ipaddress
import textwrap
import os
from urllib.parse import urlparse

def main():
    args = get_args()
    greplinks(args)


def get_args():
    Usage="""Basic usage: ./greplinks -i inputfile -o outfile \n
    \r cat inputfile | ./greplinks -o output_file"""

    #creatin custom argpatser class
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            print(Usage)
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            os._exit(2)


    # argument parse function
    def args_parser() -> 'arguments list and parser itslef':

        msg=f"""\033[1;31mThis tool is developed by Arshia Mashhoor
        \runder MIT Open source LICENCE for educational usgae only.
        \rAuthor is not responsible for any abuse!\033[0m\n{'Help':*^100}"""

        parser = MyParser(formatter_class=argparse.RawTextHelpFormatter,
                          prog="greplinks",
                          description=msg,
                          epilog=textwrap.dedent(f'''\
                                                 \r{'About':-^100}
                                                 \nAuthor: Arshia Mashhoor
                                                 \nGithub:https://github.com/a-mashhoor/greplinks
                                                 '''),
                          add_help=True,
                         )

        # if no arguments specified by the user showing the help and exiting the tool
        if len(sys.argv)==1:
            print(Usage)
            parser.print_help(sys.stderr)
            os._exit(1)

        ### Adding Command Line Arguments ###

        # input command line argumnet or file
        input_group = parser.add_mutually_exclusive_group(required=False)
        input_group.add_argument("-i", "--input-file",
                                 nargs=1,
                                 type=argparse.FileType('r', encoding='UTF-8'),
                                 help="read a inpit file")

        # simple config command line arguments
        parser.add_argument("-s", "--silent",
                            action=argparse.BooleanOptionalAction,
                            default=False,
                            help="prints nothing on stdout")

        parser.add_argument("-c", "--colored",
                            action=argparse.BooleanOptionalAction,
                            default=False,
                            help="colorize the output on stdout")

        parser.add_argument("-so", "--sort",
                            action=argparse.BooleanOptionalAction,
                            default=False,
                            help="sorts the output default False")



        # output arguments
        output_group = parser.add_mutually_exclusive_group(required=False)
        output_group.add_argument("-o", "--output",
                                  nargs=1,
                                  type=argparse.FileType('w', encoding='UTF-8'),
                                  help="save output in text (ascii based) file")

        # version command line argument
        parser.add_argument("-v", "--version", action='version', version='%(prog)s 1.0.0')

        args = parser.parse_args()

        return args

    args = args_parser()
    return args


def print_colored(text, color="green"):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "reset": "\033[0m"
    }
    print(f"{colors[color]}{text}{colors['reset']}")



def is_valid_port(port):
    try:
        port = int(port)
        return 0 <= port <= 65535
    except ValueError:
        return False


def is_valid_ipv4(ip):
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def is_valid_ipv6(ip):
    try:
        ipaddress.IPv6Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def is_valid_url(url):
    try:
        # Parse the URL
        result = urlparse(url)

        # Regex for validating domain names, IPv4, and IPv6
        domain_regex = re.compile(
            r'^(?:[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|localhost|\[[0-9a-fA-F:.]+\]|[0-9]{1,3}(?:\.[0-9]{1,3}){3})$'
        )

        # Regex for validating paths
        path_regex = re.compile(
            r'^(/[a-zA-Z0-9._~-]+(?:/[a-zA-Z0-9._~-]*)*)?$'
        )

        ipv4_regex = re.compile(
            r'^[0-9]{1,3}(?:\.[0-9]{1,3}){3}$'
        )

        # Regex for query and fragment validation
        query_regex = re.compile(r'^(\?[a-zA-Z0-9_&=.-]+)?$')
        fragment_regex = re.compile(r'^(#[a-zA-Z0-9_-]+)?$')

        # Check if the URL has a scheme and netloc
        if result.scheme and result.netloc:
            # Split netloc into host and port
            if result.netloc.startswith('['):  # IPv6 address
                host_end = result.netloc.find(']')
                if host_end == -1:
                    return False  # Invalid IPv6 format
                host = result.netloc[:host_end + 1]  # Include brackets
                port = result.netloc[host_end + 2:]  # After ']:' if port exists

                # Validate the IPv6 address
                if not is_valid_ipv6(host[1:-1]):  # Remove brackets before validation
                    return False

            else:  # IPv4 or domain name
                host, _, port = result.netloc.partition(':')

                # Validate IPv4 addresses
                if ipv4_regex.match(host):
                        if not is_valid_ipv4(host):
                            return False

            # Validate the domain (if not IPv4 or IPv6)
            if not ipv4_regex.match(host) and not is_valid_ipv6(host[1:-1]):
                if not domain_regex.match(host):
                    return False

            # Validate the port if it exists
            if port and not is_valid_port(port):
                return False

            # Validate the path
            if result.path and not path_regex.match(result.path):
                return False

            # Validate query and fragment
            if result.query and not query_regex.match(result.query):
                return False

            if result.fragment and not fragment_regex.match(result.fragment):
                return False

            return True

        # Handle URLs without a scheme (e.g., api.example.org/v1/users)
        if not result.scheme and result.path:
            # Split the path into domain and remaining parts
            parts = result.path.split('/', 1)
            domain = parts[0]
            remaining = '/' + parts[1] if len(parts) > 1 else ''

            # Split domain into host and port
            if domain.startswith('['):
                host_end = domain.find(']')
                if host_end == -1:
                    return False
                host = domain[:host_end + 1]
                port = domain[host_end + 2:]

                # Validate the IPv6 address
                if not is_valid_ipv6(host[1:-1]):  # Remove brackets before validation
                    return False
            else:
                host, _, port = domain.partition(':')

                # Validate IPv4 addresses
                if ipv4_regex.match(host):
                        if not is_valid_ipv4(host):
                            return False

            # Validate the domain (if not IPv4 or IPv6)
            if not ipv4_regex.match(host) and not is_valid_ipv6(host[1:-1]):
                if not domain_regex.match(host):
                    return False


            # Validate the domain
            if not domain_regex.match(host):
                return False

            # Validate the port if it exists
            if port and not is_valid_port(port):
                return False

            # Validate the remaining path
            if remaining and not path_regex.match(remaining):
                return False

            return True

        return False
    except:
        return False



def greplinks(args):

    file_path = args.input_file
    output_file = args.output
    silent = args.silent
    colored = args.colored
    sort = args.sort

    # Define the regex for matching URLs
    url_regex = re.compile(
        r'\b(?:https?://|wss?://|ws?://|ftp://|sftp://|scp://|tftp://|imap://|imaps://|pop://|pops://|smtp://|smtps://|rtsp://|rtsps://|rtp://|rtmp://|rtmps://|sip://|sips://|jdbc:|odbc:|mongodb://|postgres://|postgresql://|magnet:|bittorrent:|git://|ssh://|svn://|telnet://|irc://|ircs://|data:|ldap://|ldaps://|nfs://|dns://|slack://|zoommtg://|steam://|spotify:|file://)?'
        r'(?:[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|localhost|\[?[0-9a-fA-F:.]+\]?|[0-9]{1,3}(?:\.[0-9]{1,3}){3})'
        r'(?::[0-9]+)?'
        r'(?:/[^\s]*)?\b'
    )

    # Read input from file or stdin
    if file_path:
        text = file_path[0].read()
    else:
        text = sys.stdin.read()

    matches = url_regex.findall(text)

    # Process matches to remove trailing punctuation
    cleaned_urls = []
    for match in matches:
        # Remove trailing punctuation (e.g., periods, commas)
        cleaned_url = re.sub(r'[.,;!?]$', '', match)
        cleaned_urls.append(cleaned_url)

    # Filter valid URLs and sort
    valid_urls = list(set(url for url in cleaned_urls if is_valid_url(url)))

    if sort:
        valid_urls.sort()

    # Write to output file or print to console
    if output_file:
        for url in valid_urls:
            output_file[0].write(url + '\n')

    if not silent:
        for url in valid_urls:
            if colored:
                print_colored(url, color="red")
            else:
                print(url)


if __name__ == "__main__":
    main()
