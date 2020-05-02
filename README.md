# FeedMe

FeedMe provides an easy way to parse XML Feeds, render them in an HTML file, and send them based on a template to your email contacts.
 It supports tracking to send only fresh data in each run.

# Installation

Installing the application is very simple, just follow the directions below:

1. Install Python https://www.python.org/downloads/ and add it to your path
1. Install Git https://git-scm.com/downloads and add it yo your path
1. Check if you have pip (python package manager) installed by running pip --version
    1. If not, download the file [get-pip.py] (https://bootstrap.pypa.io/get-pip.py/), being careful to save it as a .py file rather than .txt
    1. Run it from the command prompt: python get-pip.py
1. Run the command pip install git+https://github.com/alimasri/feedme

# Usage

After installation, you can access the program from a command line interface using the following command:

```
$ feedme [-h] -u URL -c CONFIG [-s {google,smtp,none}] [-l LOGFILE] [-i]
              [--version] [-v] [-vv]

Arguments:

  -h, --help            show this help message and exit
  -u URL, --url URL     feed URL
  -c CONFIG, --config CONFIG
                        YAML configuration file
  -s {google,smtp,none}, --email-service {google,smtp,none}
                        email service name (none if quiet mode)
  -l LOGFILE, --log LOGFILE
                        log file path
  -i, --ignore-tracker  force feed processing even if fees was already
                        processed
  --version             show program's version number and exit
  -v, --verbose         set loglevel to INFO
  -vv, --very-verbose   set loglevel to DEBUG
```

# YAML Configuration file

FeedMe uses YAML to load the required configurations.

Create a YAML file using the following template and pass it to the (-c or --config) parameter.

```yaml
templates_folder: path to the templates folder (may contain multiple templates)
template_name: name of the template to be parsed (must be inside the templates folder)
output_folder: path to save the generated files
sender: sender's email
contacts: path to a file containing your list of recipients emails (one email per line)
credentials:
  host: smtp URL
  port: smtp port
  login: smtp login
  password: smtp password
  file: in case of choosing google service, this is the path to your credentials.json file [more info](https://developers.google.com/gmail/api/quickstart/python)
```

# Designing the Email Template

Feed me uses (Jinja)[https://jinja.palletsprojects.com/en/2.11.x/] for rendering templates.

To design an email template:

1. create an HTML file
1. use HTML language to design the static blocks of the website
1. use Jinja to load dynamic content from the feed

FeedMe passes two variables to your file
1. date: feed date
1. post: posts data each containing the following properties
    1. title: post title
    1. author: post author
    1. link: link to the original post
    1. summary: post summary