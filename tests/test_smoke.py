from __future__ import annotations

import pytest


def test_public_api_importable() -> None:
    import url_monitor

    assert callable(url_monitor.run_monitor)
    assert callable(url_monitor.save_outputs)


def test_cli_help_exits_zero(capsys) -> None:
    from url_monitor.cli import build_parser

    # argparse exits with SystemExit(0) on --help
    with pytest.raises(SystemExit) as excinfo:
        build_parser().parse_args(["--help"])
    assert excinfo.value.code == 0
    capsys.readouterr()


def test_cli_parser_defaults() -> None:
    from url_monitor.cli import build_parser

    # parse_args([]) avoids reading pytest/CI flags from sys.argv
    args = build_parser().parse_args([])

    assert args.input == "urls.txt"
    assert args.out == "report.md"
    assert args.out_dir is None
    assert args.timeout == 5.0
    assert args.strict is False
