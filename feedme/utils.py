from datetime import datetime


def parse_contacts(contacts_file):
    contacts = []
    with open(contacts_file, "r") as f:
        for line in f.readlines():
            if line == "":
                continue
            try:
                name, email = line.split(",")
                contacts.append(f"{name.strip()} <{email.strip()}>")
            except:
                pass
    return contacts


def parse_posts(feed):
    posts = []
    for entry in feed.entries:
        post_title = entry.title
        post_author = entry.author
        post_link = entry.link
        post_summary = entry.summary
        posts.append({
            "title": post_title,
            "author": post_author,
            "link": post_link,
            "summary": post_summary
        })
    return posts


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
