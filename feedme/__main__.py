import argparse
import logging
import pathlib
import sys
import feedparser
import yaml
from jinja2 import FileSystemLoader, Environment
from feedme.emailclients.google import GoogleClient
from feedme.emailclients.smtp import SMTPClient
from feedme.utils import set_tracker_datetime, parse_contacts, get_tracker_datetime
from datetime import datetime
from feedme import __version__
import webbrowser


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url",
                        dest="url",
                        help="feed URL",
                        required=True)
    parser.add_argument("-c", "--config",
                        dest="config",
                        help="YAML configuration file",
                        required=True)
    parser.add_argument("-s", "--email-service",
                        dest="client",
                        help="email service name (none if quiet mode)",
                        required=False,
                        default="none",
                        choices=["google", "smtp", "none"])
    parser.add_argument("-l", "--log",
                        dest="logfile",
                        help="log file path",
                        required=False)
    parser.add_argument("-i", "--ignore-tracker",
                        dest="ignore_tracker",
                        action='store_true',
                        help="force feed processing even if feed was already processed",
                        required=False)
    parser.add_argument("--version",
                        action="version",
                        version=f"feedme {__version__}")
    parser.add_argument('-v', '--verbose',
                        dest="loglevel",
                        help="set loglevel to INFO",
                        action='store_const',
                        const=logging.INFO)
    parser.add_argument('-vv', '--very-verbose',
                        dest="loglevel",
                        help="set loglevel to DEBUG",
                        action='store_const',
                        const=logging.DEBUG)
    return parser.parse_args(args)


logger = logging.getLogger("FeedMe")
LOG_FORMAT = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"


def setup_logging(loglevel=logging.INFO, log_file_path=None):
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    if log_file_path:
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

    try:
        feed_datetime = datetime.strptime(feed["updated"], "%a, %d %b %Y %H:%M:%S %z")
        tracker_datetime = get_tracker_datetime(output_folder)
    except:
        feed_datetime = None
        tracker_datetime = None

    if (not ignore_tracker) and \
            (feed_datetime is not None) \
            and (tracker_datetime is not None) \
            and (tracker_datetime >= feed_datetime):
        logger.info("Feed already processed")
        return

    logger.info(f"Found {nb_entries} posts")

    logger.info(f"Loading template {template_name}...")
    file_loader = FileSystemLoader(templates_folder)
    env = Environment(loader=file_loader)
    try:
        template = env.get_template(template_name + ".html")
    except:
        logger.error("Template not found!")
        return

    logger.info("Rendering...")
    date = datetime.today()
    html = template.render(date=date, posts=feed.entries, feed=feed.feed)

    html_output_path = output_folder.joinpath(f"{date.strftime('%Y%m%d%H%M%S')}.html")
    logger.info(f"Saving generated file to {html_output_path}")
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html)
    try:
        webbrowser.open(html_output_path, new=2)
    except:
        pass

    if email_client:
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


def run():
    args = parse_args(sys.argv[1:])
    setup_logging(args.loglevel, args.logfile)
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


if __name__ == "__main__":
    run()
