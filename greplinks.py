#!/usr/bin/env python3
import argparse
import re
import sys
import ipaddress
import textwrap
import os
import socket
import urllib.request
from urllib.parse import urlparse

TLD_CACHE_PATH = os.path.expanduser("~/.tld_cache.txt")

FALLBACK_TLDS = {
    "com", "net", "org", "edu", "gov", "mil", "int", "info", "biz", "co",
    "io", "dev", "ai", "me", "us", "uk", "ca", "au", "de", "fr", "jp", "cn",
    "ru", "xyz", "top", "site", "online", "app", "shop", "blog", "tech", "pro",
    "club", "store", "space", "cloud", "world", "life",
}


def main():
    args = get_args()
    greplinks(args)


def get_args():
    Usage = """Basic usage: ./greplinks -i inputfile -o outfile \n
    \r cat inputfile | ./greplinks -o output_file"""

    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            print(Usage)
            sys.stderr.write("error: %s\n" % message)
            self.print_help()
            os._exit(2)

    def args_parser():
        msg = f"""\033[1;31mThis tool is developed by Arshia Mashhoor
        \runder MIT Open source LICENCE for educational usgae only.
        \rAuthor is not responsible for any abuse!\033[0m\n{'Help':*^100}"""

        parser = MyParser(
            formatter_class=argparse.RawTextHelpFormatter,
            prog="greplinks",
            description=msg,
            epilog=textwrap.dedent(
                f"""\
                    \r{'About':-^100}
                    \nAuthor: Arshia Mashhoor
                    \nGithub:https://github.com/a-mashhoor/greplinks
                """
            ),
            add_help=True,
        )

        input_group = parser.add_mutually_exclusive_group(required=False)
        input_group.add_argument(
            "-i",
            "--input-file",
            nargs=1,
            type=argparse.FileType("r", encoding="UTF-8"),
            help="read a input file",
        )

        parser.add_argument(
            "-s",
            "--silent",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="prints nothing on stdout",
        )

        parser.add_argument(
            "-c",
            "--colored",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="colorize the output on stdout",
        )

        parser.add_argument(
            "-so",
            "--sort",
            action=argparse.BooleanOptionalAction,
            default=False,
            help="sorts the output default False",
        )

        output_group = parser.add_mutually_exclusive_group(required=False)
        output_group.add_argument(
            "-o",
            "--output",
            nargs=1,
            type=argparse.FileType("w", encoding="UTF-8"),
            help="save output in text (ascii based) file",
        )

        parser.add_argument(
            "-v", "--version", action="version", version="%(prog)s 1.0.0"
        )

        args = parser.parse_args()
        return args

    return args_parser()


def print_colored(text, color="green"):
    colors = {"green": "\033[92m", "red": "\033[91m", "reset": "\033[0m"}
    print(f"{colors[color]}{text}{colors['reset']}")


def is_valid_ipv4(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def is_valid_ipv6(ip):
    try:
        ipaddress.IPv6Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def is_connected():
    """Check if there's an internet connection by pinging Cloudflare DNS."""
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=2)
        return True
    except OSError:
        return False


def fetch_tlds_from_iana():
    """Fetch TLDs from IANA or use cached file or fallback list."""
    if os.path.exists(TLD_CACHE_PATH):
        try:
            with open(TLD_CACHE_PATH, "r", encoding="utf-8") as f:
                return set(line.strip().lower() for line in f if line)
        except Exception:
            pass

    if is_connected():
        try:
            with urllib.request.urlopen(
                "https://data.iana.org/TLD/tlds-alpha-by-domain.txt", timeout=5
            ) as response:
                lines = response.read().decode("utf-8").splitlines()
                tlds = set(
                    line.strip().lower()
                    for line in lines
                    if line and not line.startswith("#")
                )
                with open(TLD_CACHE_PATH, "w", encoding="utf-8") as f:
                    for tld in sorted(tlds):
                        f.write(tld + "\n")
                return tlds
        except Exception:
            pass

    return FALLBACK_TLDS


VALID_TLDS = fetch_tlds_from_iana()


def has_valid_tld(domain: str) -> bool:
    """Check if domain has a valid TLD."""
    if "." not in domain:
        return False
    tld = domain.rsplit(".", 1)[-1].lower()
    return tld in VALID_TLDS


def is_valid_url(url):
    """Simplified URL validation that's more permissive."""
    try:
        # Basic URL structure check
        if not url or len(url) < 3:
            return False

        # Parse the URL
        result = urlparse(url)

        # If no scheme and no netloc, try to parse as domain/path
        if not result.scheme and not result.netloc:
            # Check if it starts with a domain-like pattern
            if '/' in url:
                domain_part = url.split('/')[0]
            else:
                domain_part = url

            # Check if domain_part looks like a domain or IP
            if ':' in domain_part:
                host, port = domain_part.rsplit(':', 1)
                try:
                    port_num = int(port)
                    if not (0 <= port_num <= 65535):
                        return False
                except ValueError:
                    return False
            else:
                host = domain_part

            # Validate host
            if is_valid_ipv4(host) or is_valid_ipv6(host):
                return True
            elif '.' in host and has_valid_tld(host):
                return True
            else:
                return False

        # If we have a scheme, validate the netloc
        if result.scheme and result.netloc:
            # Extract host from netloc (handle port)
            host = result.netloc.split('@')[-1]  # Remove auth if present
            host = host.split(':')[0]  # Remove port

            # Handle IPv6 addresses in brackets
            if host.startswith('[') and host.endswith(']'):
                host = host[1:-1]

            # Validate host
            if is_valid_ipv4(host) or is_valid_ipv6(host):
                return True
            elif has_valid_tld(host):
                return True
            elif host == 'localhost':
                return True
            else:
                return False

        return False

    except Exception:
        return False


def greplinks(args):
    file_path = args.input_file
    output_file = args.output
    silent = args.silent
    colored = args.colored
    sort = args.sort

    # Improved URL regex - more permissive
    url_regex = re.compile(
        r"""(
            (?:https?|ftp|ws|wss)://[^\s<>"{}|\\^`\[\]]+ |  # URLs with scheme
            (?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}  # Domains
            (?:[/?#][^\s<>"{}|\\^`\[\]]*)?  # Optional path/query/fragment
        )""",
        re.VERBOSE
    )

    # Read input from file or stdin
    if file_path:
        text = file_path[0].read()
    else:
        text = sys.stdin.read()

    matches = url_regex.findall(text)

    # Process matches to remove trailing punctuation and clean up
    cleaned_urls = []
    for match in matches:
        if isinstance(match, tuple):
            match = match[0]  # Handle regex groups

        # Clean the URL
        cleaned_url = match.strip()

        # Remove common trailing characters
        cleaned_url = re.sub(r'[.,;!?)\]}<>]+$', '', cleaned_url)

        # Ensure URL has scheme if it looks like a domain
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', cleaned_url):
            if '/' in cleaned_url:
                # It has a path, assume http
                cleaned_url = 'http://' + cleaned_url
            elif ':' in cleaned_url.split('/')[0]:
                # It has a port, assume http
                cleaned_url = 'http://' + cleaned_url

        cleaned_urls.append(cleaned_url)

    # Filter valid URLs and remove duplicates
    valid_urls = []
    seen = set()

    for url in cleaned_urls:
        if url not in seen and is_valid_url(url):
            valid_urls.append(url)
            seen.add(url)

    if sort:
        valid_urls.sort()

    # Write to output file or print to console
    if output_file:
        for url in valid_urls:
            output_file[0].write(url + "\n")

    if not silent:
        for url in valid_urls:
            if colored:
                print_colored(url, color="green")
            else:
                print(url)


if __name__ == "__main__":
    main()
