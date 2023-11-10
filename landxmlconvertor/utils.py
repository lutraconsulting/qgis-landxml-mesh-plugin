import configparser
import pathlib


def _read_metadata() -> configparser.ConfigParser:
    path = pathlib.Path(__file__).parent / "metadata.txt"

    config = configparser.ConfigParser()
    config.read(path)

    return config


def plugin_version() -> str:
    """Get plugin version."""
    config = _read_metadata()
    return config["general"]["version"]


def plugin_repository_url() -> str:
    """Get plugin repository url"""
    config = _read_metadata()
    return config["general"]["repository"]


def plugin_author() -> str:
    """Get plugin author"""
    config = _read_metadata()
    return config["general"]["author"]
