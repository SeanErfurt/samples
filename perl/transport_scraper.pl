#!/usr/local/bin/perl -w

#
# This program walks through HTML pages, extracting all the links to other
# text/html pages and then walking those links. Basically the robot performs
# a breadth first search through an HTML directory structure.
#
# Example:
#
#    transport_scraper.pl mylogfile.log content.txt http://www.cs.jhu.edu/
#
# Note: you must use a command line argument of http://some.web.address
#       or else the program will fail with error code 404 (document not
#       found).

use strict;

use Carp;
use FileHandle;
use HTML::LinkExtor;
use HTML::TokeParser;
use HTTP::Request;
use HTTP::Response;
use HTTP::Status;
use LWP::RobotUA;
use URI::URL;
use List::Util('sum');

URI::URL::strict( 1 );   # ensure that we only traverse well formed URL's

$| = 1;

my $log_file = shift (@ARGV);
my $content_file = shift (@ARGV);
if ((!defined ($log_file)) || (!defined ($content_file))) {
    print STDERR "You must specify a log file, a content file and a base_url\n";
    print STDERR "when running the web robot:\n";
    print STDERR "  ./transport_scraper.pl mylogfile.log content.txt base_url\n";
    exit (1);
}

open LOG, ">>$log_file";
open CONTENT, ">>$content_file";
print LOG "\n[NEW RUN]\n\n";
print CONTENT "\n[NEW RUN]\n\n";
############################################################

my $ROBOT_NAME = 'serfurt1Bot/1.0';
my $ROBOT_MAIL = 'serfurt1@cs.jhu.edu';

#
# create an instance of LWP::RobotUA.
#
# Note: the LWP::RobotUA delays a set amount of time before contacting a
#       server again. The robot will first contact the base server (www.
#       servername.tag) to retrieve the robots.txt file which tells the
#       robot where it can and can't go. It will then delay. The default
#       delay is 1 minute (which is what I am using). You can change this
#       with a call of
#
#         $robot->delay( $ROBOT_DELAY_IN_MINUTES );
#

my $robot = new LWP::RobotUA $ROBOT_NAME, $ROBOT_MAIL;
$robot->delay( 0.5 );

my $base_url    = shift(@ARGV);   # the root URL we will start from

my @search_urls = ();    # current URL's waiting to be traversed
my @wanted_urls = ();    # URL's which contain info that we are looking for
my @wanted_imgs = ();    # URL's which contain images of routes we want
my %relevance   = ();    # how relevant is a particular URL to our search
my %pushed      = ();    # URL's which have either been visited or are already
                         #  on the @search_urls array
my %common_words = ();   # words to not include in frequency analysis
# words that are highly relevant in any context
my %keywords = (
    'transport' => 1,
    'transportation' => 1,
    'shuttle' => 1,
    'shuttles' => 1,
    'route' => 1,
    'routes' => 1,
    'map' => 1,
    'maps' => 1,
    'schedule' => 1,
    'schedules' => 1,
    'van' => 1,
    'vans' => 1,
);
close LOG;
close CONTENT;

#initialize common_words hash
my $common_fh = new FileHandle "common_words" , "r"
    or croak "Couldnt open common_words";
while (defined(my $line = <$common_fh>)){
    chomp $line;
    $common_words{$line} = 1;
}

push @search_urls, $base_url;


while (@search_urls) {
    # append mode
    open LOG, ">>$log_file";
    open CONTENT, ">>$content_file";

    my $url = shift @search_urls;

    #
    # ensure that the URL is well-formed, otherwise skip it
    # if not or something other than HTTP
    #

    my $parsed_url = eval { new URI::URL $url; };

    next if $@;
    next if $parsed_url->scheme !~/http/i;

    #
    # get header information on URL to see it's status (exis-
    # tant, accessible, etc.) and content type. If the status
    # is not okay or the content type is not what we are
    # looking for skip the URL and move on
    #

### request here ###
    print LOG "[HEAD ] $url\n";

    my $request  = new HTTP::Request HEAD => $url;
    my $response = $robot->request( $request );

    next if $response->code != RC_OK;
    next if ! &wanted_content( $response->content_type, $url );

    print LOG "[GET  ] $url\n";

    $request->method( 'GET' );
    $response = $robot->request( $request );

    next if $response->code != RC_OK;
    next if $response->content_type !~ m@text/html@;

    ## only act on text here ##
    print LOG "[LINKS] $url\n";
    print LOG "[URLS]\n";
    print LOG join("\n", @search_urls), "\n";

    &extract_content ($response->content, $url);

    my @related_urls  = &grab_urls( $response->content );

    foreach my $link (@related_urls) {
        my $full_url = eval { (new URI::URL $link, $response->base)->abs; };

        delete $relevance{ $link } and next if $@;

        $relevance{ $full_url } = $relevance{ $link };
        delete $relevance{ $link } if $full_url ne $link;

        my $uri = URI->new( $full_url );
        my $domain = $uri->host;
        my $baseuri = URI->new( $response->base );
        my $basedomain = $baseuri->host;

        #if link is unvisited/unpushed and local, do something
        if (! exists $pushed{ $full_url } && $domain =~ $basedomain ) {
            push @search_urls, $full_url and $pushed{ $full_url } = 1;
        }

    }

    ## handle images ##
    while (@wanted_imgs) {
        my $img = shift @wanted_imgs;
        &extract_route($img);
    }
    ## handle urls ##
    while (@wanted_urls) {
        my $link = shift @wanted_urls;
        &extract_info($link);
    }

    #force write for this iteration (reopens in append)
    close LOG;
    close CONTENT;

    #
    # reorder the urls base upon relevance so that we search
    # areas which seem most relevant to us first.
    #

    @search_urls =
    sort { $relevance{ $a } <=> $relevance{ $b }; } @search_urls;
}

exit (0);

#
# wanted_content
#
#  this function checks to see if the current MIME content type
#  is something which is either
#
#    a) something we are looking for (e.g. postscript, pdf,
#       plain text, or html). In this case we should save the URL in the
#       @wanted_urls array.
#
#    b) something we can traverse and search for links
#       (this can be just text/html).
#

sub wanted_content {
    my $c_type = shift;
    my $url = shift;
    my $result = 0;

    #if ($url =~ /^http/ && $url !~ /\/#/) {
        if ($c_type =~ m@text/html@ ) {
            $result = $c_type;
            push @wanted_urls, $url;
        } elsif (($c_type =~ m@application/pdf@) || ($c_type =~ m@image/png@) || ($c_type =~ m@image/jpeg@)) {
            $result = $c_type;
            push @wanted_imgs, $url;
        }
    #}
    return $result;
}

#
# extract_content
#
#  this function reads through the context of all the text/html
#  documents retrieved by the web robot and extract three types of
#  contact information

sub extract_content {

    my $content = shift;
    my $url = shift;
    my $copy1 = $content;
    my $copy2 = $content;
    my $copy3 = $content;

    my $phone;
    my $email;
    my $address;

    # parse out information you want
    # print it in the tuple format to the CONTENT and LOG files, for example:

    while ($copy1 =~ s/(\w+@\w+\.\w+(\.\w+){0,1})//)
    {
        $email = $1;
        print CONTENT "($url; EMAIL; $email)\n";
        #print LOG "($url; EMAIL; $email)\n";
        print "EMAIL: ", $email, "\n";
    }

    while ($copy2 =~ s/\D((\d{3}){0,1}(\(\d{3}\)){0,1}\D\d{3}\D\d{4})\D//)
    {
        $phone = $1;
        print CONTENT "($url; PHONE; $phone)\n";
        #print LOG "($url; PHONE; $phone)\n";
        print "PHONE: ", $phone, "\n";
    }

    while ($copy3 =~ s/([A-Za-z]+,{0,1}\s[A-Za-z]+,{0,1}\s\d{5}(.\d{4}){0,1})//)
    {
        $address = $1;
        print CONTENT "($url; ADDRESS; $address)\n";
        #print LOG "($url; ADDRESS; $address)\n";
        print "ADDRESS: ", $address, "\n";
    }

    return;
}

# TODO These are stubs. Visit the reported urls and tailor the extraction code
#       to a general version of their HTML formats
# process an image for route stop information
sub extract_route {
    my $url = shift;
    print CONTENT "[WANTED IMG] $url\n";
    return;
}

# process a wanted_url for useful information
sub extract_info {
    my $url = shift;
    print CONTENT "[WANTED URL] $url\n";
    return;
}

#
# grab_urls
#
#   this function parses through the content of a passed HTML page and
#   picks out all links and any immediately related text.
#
#   Example:
#
#     given
#
#       <a href="somepage.html">This is some web page</a>
#
#     the link "somepage.html" and related text "This is some web page"
#     will be parsed out. However, given
#
#       <a href="anotherpage.html"><img src="image.jpg">
#
#       Further text which does not relate to the link . . .
#
#     the link "anotherpage.html" will be parse out but the text "Further
#     text which . . . " will be ignored.
#
#   Our relevance is calculated based on whether the related text contains
#       words that are commonly found elsewhere (excluding stopwords)
#       in the html document, weighted towards more frequent words, and
#       normalized by number of words in related text.
#
#   Example:
#
#      $relevance{ $link } = &your_relevance_method( $link, $text );
#

sub grab_urls {
    my $content = shift;
    my %urls    = ();    # NOTE: this is an associative array so that we only
                         #       push the same "href" value once.
    my %count = ();
    my $total = 0;
    #determine content topic
    my $stream = HTML::TokeParser->new( \$content )
        || die "Couldn't read content";
    while(my $token = $stream->get_token) {
        #grab plaintext
        if ($token->[0] =~ "T"){
            #normalize
            my $text = lc $token->[1];
            my @words = split ' ', $text;
            foreach my $word (@words) {
                #count if not common word
                if (!exists ($common_words{$word})){
                    $count{$word}++;
                    $total++;
                }
            }
        }
    }
    #normalize counts
    while ((my $key, my $val) = each %count) {
        $count{$key} = $val / $total;
        print LOG "[REL TOK] $key   =>  $count{$key}\n";
    }
    my $avg = sum(values %count)/ scalar(keys %count);

    while ($content =~ s/<\s*[aA] ([^>]*)>\s*(?:<[^>]*>)*(?:([^<]*)(?:<[^aA>]*>)*<\/\s*[aA]\s*>)?//) {

    	my $tag_text = $1;
    	my $reg_text = $2;
    	my $link = "";
        my $rel;

    	if (defined $reg_text) {
    	    $reg_text =~ s/[\n\r]/ /;
    	    $reg_text =~ s/\s{2,}/ /;

    	    # compute relevancy function here for related text
            $rel = 0;
            my @words = split ' ', $reg_text;
            if (scalar(@words) > 0) {
                foreach my $word (@words) {
                    if (exists ($keywords{$word})){
                        $rel = $rel + 1;
                    } elsif (exists ($count{$word})){
                        $rel = $rel + $count{$word};
                    }
                }
                #normalize by total number of words in text
                $rel = $rel / scalar(@words);
            } else {
                #if no related text, give default relevance of avg (average relevance)
                $rel = $avg;
            }
    	} else {
            $rel = $avg;
        }

    	if ($tag_text =~ /href\s*=\s*(?:["']([^"']*)["']|([^\s])*)/i) {
    	    $link = $1 || $2;

            #throw away things like "mailto:" and self-ref links
            if ($link =~ /^http/ && $link !~ /\/#/) {
        	    $relevance{ $link } = $rel;
        	    $urls{ $link }      = 1;
            }
    	}

    	print $reg_text, "\n" if defined $reg_text;
    	print $link, "\n\n";
    }

    return keys %urls;   # the keys of the associative array hold all the
                         # links we've found (no repeats).
}
