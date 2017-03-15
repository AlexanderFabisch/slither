from slither.domain_model import Activity


def test_create_activity():
    a = Activity(sport="running", distance="10000", time="3600")
