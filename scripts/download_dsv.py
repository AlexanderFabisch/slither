"""This script will download data from the DSV (german swimming federation).

last checked: 2017/03/15
"""
import sys
import mechanize
from bs4 import BeautifulSoup
import datetime
import unicodedata


class Swim(object):
    def __init__(self, stroke, time, place, date, mode):
        self.stroke = stroke
        self.time = time
        self.place = place
        self.date = date
        self.mode = mode

    def __str__(self):
        place = unicodedata.normalize("NFKD", self.place).encode("ascii", "ignore")
        return "%s;%s;%s;%s;%s" % (self.stroke, self.time, place,
                                       self.date, self.mode)


def load_search(br, swimmer_name):
    br.open("http://dsvdaten.de/Modules/Results/Individual.aspx")
    # URLs:
    # http://dsvdaten.de/Modules/Results/Individual.aspx
    # http://dsvdaten.de/Modules/Results/Archive.aspx
    # http://dsvdaten.de/Modules/Rankings/Default.aspx
    br.select_form(nr=0)
    firstname, lastname = swimmer_name.split(" ")
    br["_firstnameTextBox"] = firstname
    br["_lastnameTextBox"] = lastname
    resp = br.submit()
    return resp


def load_swimmer(br, content):
    soup = BeautifulSoup(content)
    note = soup.find(id="_noteLabel")
    if note is not None:
        note = note.text
        if "Keine Schwimmer" in note:
            return False, None
        elif "Schwimmer gefunden" in note:
            table = soup.find_all("table", attrs={"class": "1"})[0]
            rows = table.find_all("tr")
            headings = [heading.text for heading in rows[0].find_all("th")]
            chars = [25, 10, 25, 10]
            print("   " + "".join([t.ljust(c) for c, t in zip(chars, headings)]))
            rows = rows[1:]
            swimmer_links = []
            for i, row in enumerate(rows):
                entries = row.find_all("td")
                individual_url = entries[0].find("a").attrs["href"]
                swimmer_links.append(individual_url)
                nation = entries[3].find("img").attrs["src"].split("/")[-1].split(".")[0]
                entries = [entries[0].text, entries[1].text, entries[2].text, nation]
                print(("%d) " % (i + 1)) + "".join([t.ljust(c) for c, t in zip(chars, entries)]))
            selected = False
            while not selected:
                i = int(raw_input("Please select your swimmer and press 'Enter'\n"))
                if 0 < i < len(swimmer_links):
                    link = swimmer_links[i - 1]
                    resp = br.follow_link(url=link)
                    selected = True
            return False, resp
    else:
        return True, None


def load_data(content):
    soup = BeautifulSoup(content)
    contenttable = soup.find_all("table", attrs={"class": "contenttable"})[1]
    rows = contenttable.find_all("tr")
    results = []
    mode = "short"
    for r in rows[2:]:
        heading = r.find("th")
        if heading is not None:
            category = heading.text.strip().split(" ")[0]
            if category == "25":
                mode = "short"
                continue
            elif category == "50":
                mode = "long"
                continue
            elif category == "Freiwasser":
                mode = "openwater"
                continue
            elif category == "Staffelstarts":
                mode = "relay"
                continue
            else:
                raise Exception("Unknown category '%s'" % category)

        cells = r.find_all("td")
        if len(cells) != 6:
            continue

        stroke = cells[0].text.strip()
        time = cells[1].text.strip()
        place = cells[4].text.strip()
        date = datetime.datetime.strptime(cells[5].find("span").attrs["title"],
                                          "%d.%m.%Y")
        swim = Swim(stroke, time, place, date, mode)
        results.append(swim)
    return results


def main():
    if len(sys.argv) < 3:
        print("Usage: python download.py <firstname> <lastname>")
        exit(1)
    swimmer_name = " ".join(sys.argv[1:])

    br = mechanize.Browser()
    resp = load_search(br, swimmer_name)
    content = resp.read()
    success, resp = load_swimmer(br, content)
    if not success and resp is None:
        raise Exception("No swimmer found")

    br.select_form(nr=0)
    selection = br.form.controls[3]
    options = map(lambda i: i.name, selection.get_items())
    results = []
    for option in options:
        br.select_form(nr=0)
        br.form["_resultsDropDownList"] = [option]
        resp = br.submit()
        content = resp.read()
        results.extend(load_data(content))

    filename = swimmer_name.replace(" ", "_") + ".csv"
    with open(filename, "w") as f:
        for r in results:
            f.write("%s\n" % r)


if __name__ == "__main__":
    main()