# todo: Import necessary libraries
from bs4 import BeautifulSoup
import os
import re
import dateutil.parser as dparser
import csv

# todo: Parse data from web pages
path  = os.path.dirname(os.path.abspath(__file__))
pages = os.listdir('WebPages')

# loop all the files
events = []
for page in pages:
    url = r"{}\WebPages\{}".format(path, page)
    soup = BeautifulSoup(open(url, encoding ="utf8"), 'html.parser')
    event_name = soup.find(id="h1header").text
    other_details = soup.find(id="perfDesc")

    for_venue = other_details.a.text.split(": ")
    for_date = other_details.text.split(" -")
    venue_name = for_venue[0]
    event_date = for_date[1].replace("\n", "")

    entry = {
        "page": page,
        "event_name": event_name,
        "event_date": dparser.parse(event_date)
    }

    events.append(entry)

# sorted events by date
new_events = sorted(events, key=lambda k: k['event_date'])

to_csv = []
for page in new_events:
    url = r"{}\WebPages\{}".format(path, page["page"])
    soup = BeautifulSoup(open(url, encoding ="utf8"), 'html.parser')
    event_name = soup.find(id="h1header").text
    other_details = soup.find(id="perfDesc")

    for_venue = other_details.a.text.split(": ")
    for_date = other_details.text.split(" -")
    venue_name = for_venue[0]
    event_date = for_date[1].replace("\n", "")

    listings = soup.find_all(class_="listing")
    elements = []
    for listing in listings:
        price = listing.label.text
        if listing.find("option") is None:
            continue
        qty = listing.find("option")["value"]

        details = listing.find(class_="details").div.span.text.split(" • ")

        if 'Section' in details[0]:
            section = details[0].split("Section ")[1]
        elif 'Promenade Reserved' in details[0]:
            section = details[0].split("Promenade Reserved ")[1]
        else:
            section = details[0].split("PROMENADE RESERVED ")[1]
        row = details[1].split("Row ")[1]

        if listing.find(class_="details").a is None:
            notes = ""
        else:
            notes = listing.find(class_="details").a["data-displaytext"]
        stock_type = listing.find(class_="details").label.find_next("label").text

        # Event Name, Venue Name, Event Date, Section, Row, Notes, Stock Type, Quantity, Price
        entry = {
            "Event Name": event_name,
            "Venue Name": venue_name,
            "Event Date": event_date,
            "Section": section,
            "Row": row,
            "Notes": notes,
            "Stock Type": stock_type,
            "Quantity": qty,
            "Price": price.replace("$","")
        }
        elements.append(entry)

    # sort elements by price
    newlist = sorted(elements, key=lambda k: float(k['Price']))

    to_csv.append(newlist)

# todo: Write to spreadsheet
keys = to_csv[0][0].keys()
csv_file = "tickets.csv"
exist = os.path.isfile('./'+csv_file)

if(exist):
    with open(csv_file, mode='w') as csv_f:
        writer = csv.DictWriter(csv_f, fieldnames=keys)

        writer.writeheader()
        for i in range(len(to_csv)):
            writer.writerows(to_csv[i])