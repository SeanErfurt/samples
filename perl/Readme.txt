This folder contains some of the Perl scripts I wrote for my Information
Retrieval & Web Agents class.

lwp_parser.pl extracts all the image links from the web page given on
the command line and prints them to STDOUT. Good for chaining commands.

transport_scraper.pl walks through HTML pages, extracting all the links to
other text/html pages and then walking those links. Basically the robot
performs a breadth first search through an HTML directory structure. While
it can be configured to search for other keywords, currently it is written
to search for urls related to transportation(routes, maps, schedules, etc.)

common_words is used by transport_scraper.pl to filter stopwords and such.
