import argparse
import datetime
import logging
import pathlib
import sys
import feedparser
import yaml
from jinja2 import FileSystemLoader, Environment

from emailclients.google import GoogleClient
from emailclients.smtp import SMTPClient

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--url",
                    dest="url",
                    help="Feed URL",
                    required=True)
parser.add_argument("-c", "--config",
                    dest="config",
                    help="YAML configuration file",
                    required=True)
parser.add_argument("-s", "--email-service",
                    dest="client",
                    help="Name of the email service",
                    required=True,
                    choices=["google", "smtp"])
parser.add_argument("-i", "--ignore-tracker",
                    dest="ignore_tracker",
                    type=bool,
                    help="A flag to force feed processing even if fees was already processed",
                    default=False,
                    required=False)
parser.add_argument("-l", "--log",
                    dest="logfile",
                    help="Log file path",
                    required=False)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level="DEBUG", format=LOG_FORMAT)
logger = logging.getLogger("FeedMe")


def enable_file_logging(log_file_path):
    global logger
    f_handler = logging.FileHandler(log_file_path)
    f_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    f_handler.setLevel(logging.INFO)
    logger.addHandler(f_handler)


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
            return datetime.datetime.fromisoformat(date_string)
    except:
        return None


def set_tracker_datetime(template_folder, new_datetime):
    try:
        with open(template_folder.joinpath("TRACKER"), "w") as f:
            f.write(new_datetime.isoformat())
    except:
        pass


def main(url, templates_folder, template_name, output_folder, contacts_file, sender, email_client):
    logger.info(f"Parsing data from {url}")
    try:
        feed = feedparser.parse(url)
        if feed is None:
            raise
    except:
        logger.error("Unable to parse feed!")
        return

    nb_entries = len(feed.entries)
    if nb_entries == 0:
        logger.info("No entries found!")
        return

    output_folder = pathlib.Path(output_folder).joinpath(template_name)
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    feed_datetime = datetime.datetime.strptime(feed.feed["updated"], "%a, %d %b %Y %H:%M:%S %z")
    tracker_datetime = get_tracker_datetime(output_folder)

    if (feed_datetime is not None) \
            and (tracker_datetime is not None) \
            and (tracker_datetime >= feed_datetime):
        logger.info("Feed already processed")
        return

    logger.info(f"Found {nb_entries} posts")
    posts = parse_posts(feed)

    logger.info(f"Loading template {template_name}...")
    file_loader = FileSystemLoader(templates_folder)
    env = Environment(loader=file_loader)
    try:
        template = env.get_template(template_name + ".html")
    except:
        logger.error("Template not found!")
        return

    logger.info("Rendering...")
    date = datetime.datetime.today().strftime("%Y%m%d")
    html = template.render(date=date, posts=posts)

    html_output_path = output_folder.joinpath(f"{date}.html")
    logger.info(f"Saving generated file to {html_output_path}")
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"Parsing contacts from {contacts_file}")
    contacts = parse_contacts(contacts_file)

    logger.info("Sending email...")
    subject = f"{template_name} Posts"
    to = ','.join(contacts)
    message = email_client.create_message(sender, to, subject, html)
    email_client.send_message(message)

    if feed_datetime is not None:
        logger.info("Setting tracker info...")
        set_tracker_datetime(output_folder, feed_datetime)


if __name__ == "__main__":
    args = parser.parse_args(sys.argv[1:])
    if args.logfile:
        enable_file_logging(args.logfile)
    logger.info("Program Started")
    config = yaml.load(open(args.config, "r"), Loader=yaml.FullLoader)
    client = None
    credentials = config["credentials"]
    if args.client == "google":
        client = GoogleClient(credentials["file"])
    elif args.client == "smtp":
        client = SMTPClient(credentials["host"],
                            credentials["port"],
                            credentials["login"],
                            credentials["password"])
    else:
        logger.error("Email client not supported")
        exit(1)
    main(args.url,
         config["templates_folder"],
         config["template_name"],
         config["output_folder"],
         config["contacts"],
         config["sender"],
         client)
    logger.info("Program terminated successfully")
