from datetime import datetime


def parse_contacts(contacts_file):
    contacts = []
    with open(contacts_file, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line == "":
                continue
            try:
                name, email = line.split(",")
                contacts.append(f"{name.strip()} <{email.strip()}>")
            except:
                contacts.append(line)
    return contacts


def get_tracker_datetime(template_folder):
    try:
        with open(template_folder.joinpath("TRACKER"), "r") as f:
            date_string = f.readline()
            return datetime.fromisoformat(date_string)
    except:
        return None


def set_tracker_datetime(template_folder, new_datetime):
    try:
        with open(template_folder.joinpath("TRACKER"), "w") as f:
            f.write(new_datetime.isoformat())
    except:
        pass
