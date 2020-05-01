import argparse
import logging
import pathlib
import sys
import feedparser
import yaml
from jinja2 import FileSystemLoader, Environment
from feedme.emailclients.google import GoogleClient
from feedme.emailclients.smtp import SMTPClient
from feedme.utils import set_tracker_datetime, parse_posts, parse_contacts, get_tracker_datetime
from datetime import datetime

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
                    help="Name of the email service (none if quiet mode)",
                    required=False,
                    default="none",
                    choices=["google", "smtp", "none"])
parser.add_argument("-l", "--log",
                    dest="logfile",
                    help="Log file path",
                    required=False)
parser.add_argument("-i", "--ignore-tracker",
                    dest="ignore_tracker",
                    action='store_true',
                    help="A flag to force feed processing even if fees was already processed",
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


def main(url, templates_folder, template_name, output_folder, contacts_file, sender, email_client, ignore_tracker):
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

    feed_datetime = datetime.strptime(feed.feed["updated"], "%a, %d %b %Y %H:%M:%S %z")
    tracker_datetime = get_tracker_datetime(output_folder)

    if (not ignore_tracker) and \
            (feed_datetime is not None) \
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
    date = datetime.today().strftime("%Y%m%d")
    html = template.render(date=date, posts=posts)

    html_output_path = output_folder.joinpath(f"{date}.html")
    logger.info(f"Saving generated file to {html_output_path}")
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html)

    if client:
        logger.info(f"Parsing contacts from {contacts_file}")
        contacts = parse_contacts(contacts_file)
        if len(contacts) == 0:
            logger.info("No contacts found!")
        else:
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
    elif args.client == "none":
        client = None
    else:
        logger.error("Email client not supported")
        exit(1)
    main(args.url,
         config["templates_folder"],
         config["template_name"],
         config["output_folder"],
         config["contacts"],
         config["sender"],
         client,
         args.ignore_tracker)
    logger.info("Program terminated successfully")
