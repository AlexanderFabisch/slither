import os

from pkg_resources import resource_filename

config = {
    "sports":
        ["swimming",
         "running",
         "racecycling",
         "cycling",
         "other"],
    "pace_distance_table":
        {"swimming": 100.0,
         "running": 1000.0,
         "racecycling": 1000.0,
         "cycling": 1000.0,
         "other": 1000.0
         },
    "records":
        {"running":
            [400.0, 800.0, 1000.0, 1500.0, 5000.0, 10000.0, 21097.5, 42195.0],
         "swimming":
            [50.0, 100.0, 200.0, 400.0, 800.0, 1500.0],
         "racecycling":
            [1000.0, 20000.0, 40000.0, 90000.0, 180000.0]
         },
    "max_velocity":
        {"swimming": 5,
         "running": 18,
         "racecycling": 30,
         "cycling": 30,
         "default": 50},
    "velocity_thresholds":
        {"running":
             [1.39,  1.81,  2.22,  2.64,  3.06,  3.47,  3.89,  4.31,  4.72],
         "racecycling":
             [2.22, 3.33, 4.44, 5.56, 6.67, 7.78, 8.89, 10., 11.11],
         "cycling":
             [2.22, 3.33, 4.44, 5.56, 6.67, 7.78, 8.89, 10., 11.11],
         "other": [2.22, 3.33, 4.44, 5.56, 6.67, 7.78, 8.89, 10., 11.11]},
    "plot":
        {"filter_width": 31},
    "colors":
        ["#0000FF", "#0040FF", "#0080FF", "#00FFB0", "#00E000", "#80FF00",
         "#FFFF00", "#FFC000", "#FF0000"]
}


def slither_ressource_filename(filename):
    return resource_filename("slither", os.path.join("resources", filename))