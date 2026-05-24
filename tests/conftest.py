import pytest
from mcp_server.data import load_dataset


@pytest.fixture(scope="session")
def df():
    return load_dataset("docs/1900_2021_DISASTERS_Example.csv")
