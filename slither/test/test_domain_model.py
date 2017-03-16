import numpy as np
from slither.domain_model import Activity, Trackpoint
from nose.tools import assert_equal


def test_create_activity():
    a = Activity(sport="running", distance="10000", time="3600",
                 has_path=True)
    n_steps = 100
    a.set_path(
        timestamps=np.arange(n_steps),
        coords=np.vstack((np.linspace(0, np.pi, n_steps),
                          np.linspace(0, np.pi, n_steps))).T,
        altitudes = np.zeros(n_steps),
        heartrates=np.zeros(n_steps),
        velocities=np.zeros(n_steps)
    )
    path = a.get_path()
    assert_equal(len(path["timestamps"]), n_steps)
