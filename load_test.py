"""Run a bounded HTTP load test against an explicitly selected target."""

import argparse
import ipaddress
import math
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from urllib.parse import urlparse

import requests


SCENARIOS = {
    "normal": (20, 30),
    "medium": (50, 30),
    "high": (100, 60),
}


@dataclass
class WorkerResult:
    total: int = 0
    successful: int = 0
    failed: int = 0


def run_worker(url: str, deadline: float, timeout: float) -> WorkerResult:
    result = WorkerResult()
    while time.monotonic() < deadline:
        try:
            response = requests.get(url, timeout=timeout)
            result.total += 1
            if 200 <= response.status_code < 400:
                result.successful += 1
            else:
                result.failed += 1
        except requests.RequestException:
            result.total += 1
            result.failed += 1
    return result


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0 or parsed > 60:
        raise argparse.ArgumentTypeError("must be greater than zero and at most 60")
    return parsed


def local_http_url(value: str) -> str:
    try:
        parsed = urlparse(value)
        hostname = parsed.hostname
        parsed.port
    except ValueError as error:
        raise argparse.ArgumentTypeError("invalid target URL: {}".format(error))

    if (
        parsed.scheme not in ("http", "https")
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise argparse.ArgumentTypeError("target must be an HTTP(S) URL without credentials")

    try:
        is_loopback = ipaddress.ip_address(hostname).is_loopback
    except ValueError:
        is_loopback = hostname.lower() == "localhost"
    if not is_loopback:
        raise argparse.ArgumentTypeError("target must use localhost or a loopback IP")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send bounded concurrent GET requests to a target URL."
    )
    parser.add_argument(
        "--url",
        type=local_http_url,
        default="http://127.0.0.1:5002/",
        help="Target URL (default: %(default)s)",
    )
    parser.add_argument(
        "--scenario",
        choices=tuple(SCENARIOS),
        default="normal",
        help="Preset scenario; --users and --duration override its values",
    )
    parser.add_argument("--users", type=positive_int, help="Number of concurrent users")
    parser.add_argument("--duration", type=positive_int, help="Test duration in seconds")
    parser.add_argument(
        "--timeout",
        type=positive_float,
        default=5.0,
        help="Per-request timeout in seconds (default: %(default)s)",
    )
    args = parser.parse_args()
    if args.users is not None and args.users > 100:
        parser.error("--users cannot exceed 100")
    if args.duration is not None and args.duration > 60:
        parser.error("--duration cannot exceed 60 seconds")
    preset_users, preset_duration = SCENARIOS[args.scenario]
    args.users = args.users or preset_users
    args.duration = args.duration or preset_duration
    return args


def main() -> None:
    args = parse_args()
    started_at = time.monotonic()
    deadline = started_at + args.duration

    with ThreadPoolExecutor(max_workers=args.users) as executor:
        futures = [
            executor.submit(run_worker, args.url, deadline, args.timeout)
            for _ in range(args.users)
        ]
        results = [future.result() for future in futures]

    elapsed = time.monotonic() - started_at
    total = sum(result.total for result in results)
    successful = sum(result.successful for result in results)
    failed = sum(result.failed for result in results)

    print("Load test summary")
    print("Target URL:       {}".format(args.url))
    print("Scenario:         {}".format(args.scenario))
    print("Virtual users:    {}".format(args.users))
    print("Requested length: {} seconds".format(args.duration))
    print("Actual elapsed:   {:.2f} seconds".format(elapsed))
    print("Total requests:   {}".format(total))
    print("Successful:       {}".format(successful))
    print("Failed:           {}".format(failed))
    print("Requests/second:  {:.2f}".format(total / elapsed if elapsed else 0))


if __name__ == "__main__":
    main()
