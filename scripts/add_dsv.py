"""Stores data downloaded from the DSV website in the database."""
import argparse
import pandas as pd
import numpy as np
from rich.progress import Progress
from slither.service import Service


def main():
    args = parse_args()
    fill_database(args)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename",
                        help="CSV file that contains the results of a swimmer")
    parser.add_argument("--debug", help="Start debug mode", action="store_true")
    parser.add_argument("--datadir", type=str, default="data",
                        help="Directory to store files")
    parser.add_argument("--db_filename", type=str, default="db.sqlite",
                        help="Filename of SQLite database")
    parser.add_argument("--base_path", type=str, default=None,
                        help="Base path in which data will be stored. "
                             "This will be ~/.slither by default.")
    args = parser.parse_args()
    return args


def fill_database(args):
    s = Service(debug=args.debug, datadir=args.datadir,
                db_filename=args.db_filename, base_path=args.base_path)
    data = read_data(args.filename)
    with Progress() as progress:
        task = progress.add_task("Data import", total=len(data))
        for row in data.iterrows():
            progress.console.print("Importing:\n%s" % (row,))
            progress.advance(task)
            row = row[1]
            try:
                distance = distance_from_stroke(row["Stroke"])
                time = row["Time"]
                if not np.isfinite(time):
                    raise Exception(time)

                activities = s.list_activity_for_date(row["Date"])
                duplicate = False
                for a in activities:
                    if a.time == time and a.distance == distance:
                        progress.console.print("Duplicate entry, ignored.")
                        duplicate = True
                        break
                if duplicate:
                    progress.console.print("[red]Found similar activity, ignored.[/red]")
                    continue

                metadata = {"sport": "swimming",
                            "start_time": row["Date"],
                            "distance": distance,
                            "time": time,
                            "filetype": "",
                            "has_path": False}
                s.new_activity(metadata)
            except Exception as e:
                progress.console.print(e)


def read_data(filename):
    df = pd.read_csv(filename, sep=";", na_values=["NA", "AB", "DS"],
                     names=["Stroke", "Time", "Place", "Date", "Mode"],
                     parse_dates=[3])
    df["Time"] = df["Time"].apply(convert_time)
    return df


def convert_time(t):
    if isinstance(t, str):
        r = t.split(" ")
        if len(r) > 1:
            hours = int(r[0].replace("h", ""))
            t = r[1]
        first, h = t.split(",")
        parts = first.split(":")
        parts = list(map(int, parts))
        seconds = 60 * parts[0] + parts[1]
        return float(seconds) + float(h) / 100.0
    else:
        return t


def distance_from_stroke(stroke):
    if stroke in ["50R", "50S", "50B", "50F"]:
        return 50.0
    elif stroke in ["100R", "100D", "100B", "100F", "100L"]:
        return 100.0
    elif stroke in ["200R", "200D", "200B", "200F", "200L"]:
        return 200.0
    elif stroke in ["400R", "400D", "400B", "400F", "400L"]:
        return 400.0
    elif stroke in ["800F"]:
        return 800.0
    elif stroke in ["1500F"]:
        return 1500.0
    elif stroke in ["2500F"]:
        return 2500.0
    else:
        raise Exception("Unrecognized stroke '%s'" % stroke)


if __name__ == '__main__':
    main()
