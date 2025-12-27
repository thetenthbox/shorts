from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="shorts")
    p.add_argument("--id", required=True)
    p.add_argument("--audio", help="Path to audio script md")
    p.add_argument("--topic", help="Topic prompt")
    return p


def main(argv=None) -> int:
    _ = build_parser().parse_args(argv)
    # Orchestrator implementation comes next; tests focus on components first.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


