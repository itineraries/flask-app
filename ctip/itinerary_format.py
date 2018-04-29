import cgi, datetime, dateutil.parser, os.path, pytz, sys
from flask import Flask, request

for sam_dir in (
    # ./scheduler-and-mapper/
    os.path.join(os.path.dirname(__file__), "scheduler-and-mapper"),
    # ../scheduler-and-mapper/
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "scheduler-and-mapper"
    )
):
    # Look for the scheduler-and-mapper directory.
    if os.path.isdir(sam_dir):
        # Use the first one that is found.
        sys.path.insert(1, sam_dir)
        break
import agency_nyu, agency_walking, agency_walking_static, \
    agency_walking_dynamic, departure_lister, itinerary_finder, stops
TIME_FORMAT = "%I:%M %p on %A"
TIMEZONE = pytz.timezone("America/New_York")

agencies = (
    agency_nyu.AgencyNYU,
    agency_walking_static.AgencyWalkingStatic,
    agency_walking_dynamic.AgencyWalkingDynamic,
)
agencies_to_vary = (
    agency_nyu.AgencyNYU,
)

weekdays = tuple(
    # Sunday to Saturday
    datetime.date(2006, 1, d).strftime("%A") for d in range(1, 8)
)

def days_hours_minutes(td):
    '''
    Breaks a datetime.timedelta into the days as an integer, the hours as an
    integer, and the minutes as a float.
    '''
    return td.days, td.seconds // 3600, (td.seconds / 60) % 60
def days_hours_minutes_string(td):
    '''
    Converts a datetime.timedelta into a string that contains days, hours, and
    minutes.
    '''
    days, hours, minutes = days_hours_minutes(td)
    result = []
    if days:
        if days == 1:
            result.append("1 day")
        else:
            result.append("{} days".format(days))
    if hours:
        if hours == 1:
            result.append("1 hour")
        else:
            result.append("{} hours".format(hours))
    if minutes:
        if minutes == 1:
            result.append("1 minute")
        else:
            result.append("{:.0f} minutes".format(minutes))
    if result:
        if len(result) == 1:
            return result[0]
        if len(result) == 2:
            return result[0] + " and " + result[1]
        result[-1] = "and " + result[-1]
        return ", ".join(result)
    return "An instant"
def get_datetime_trip():
    # Combine the "day" and "when" GET parameters and parse them together.
    try:
        return dateutil.parser.parse(
            request.args.get("day", "") +
            " " +
            request.args["when"]
        )
    except (KeyError, ValueError):
        return datetime.datetime.now(TIMEZONE).replace(tzinfo=None)
def get_weekdays_checked(datetime_trip):
    # Make a list of the days of the week and select the one in datetime_trip.
    dow = (datetime_trip.weekday() + 1) % 7
    return \
        [(s, False) for s in weekdays[:dow]] + \
        [(weekdays[dow], True)] + \
        [(s, False) for s in weekdays[dow+1:]]
def mark_weighted_edge_up(edge, margin):
    '''
    Renders a weighted edge as one HTML <li> element.
    
    The margin is inserted at the beginning of every line.
    '''
    return (
        # Start the list item.
        margin + "<li>\n" + 
        # Add the human-readable instruction.
        margin + "\t" + cgi.escape(
            edge.get_human_readable_instruction()
        ) + "\n" +
        # Start the nested unordered list.
        margin + "\t<ul>\n" + 
        # Add the departure time.
        margin + "\t\t<li>\n" +
        margin + "\t\t\t<span class=\"itinerary-time\">" + cgi.escape(
            edge.datetime_depart.strftime(TIME_FORMAT)
        ) + ":</span>\n" +
        margin + "\t\t\tDepart from\n" +
        margin + "\t\t\t<span class=\"itinerary-node\">" + cgi.escape(
            edge.from_node
        ) + "</span>.\n" +
        margin + "\t\t</li>\n" +
        # Add the list of intermediate nodes.
        (
            (
                # Start the list item.
                margin + "\t\t<li>\n" +
                # Add the heading for the nested list.
                margin + "\t\t\tIntermediate stops:\n" +
                # Start the nested ordered list.
                margin + "\t\t\t<ol>\n" +
                # Add the list items.
                "".join(
                    margin + "\t\t\t\t<li>\n" +
                    margin + "\t\t\t\t\t<span class=\"itinerary-time\">" +
                    cgi.escape(
                        node_and_time.time.strftime(TIME_FORMAT)
                    ) + ":</span>\n" +
                    margin + "\t\t\t\t\t<span class=\"itinerary-node\">" +
                    cgi.escape(node_and_time.node) + "</span>\n" +
                    margin + "\t\t\t\t</li>\n"
                    for node_and_time in edge.intermediate_nodes
                ) +
                # End the nested ordered list.
                margin + "\t\t\t</ol>\n" +
                # End the list item.
                margin + "\t\t</li>\n"
            )
            if edge.intermediate_nodes else
            ""
        ) +
        # Add the arrival time.
        margin + "\t\t<li>\n" +
        margin + "\t\t\t<span class=\"itinerary-time\">" + cgi.escape(
            edge.datetime_arrive.strftime(TIME_FORMAT)
        ) + ":</span>\n" +
        margin + "\t\t\tArrive at\n" +
        margin + "\t\t\t<span class=\"itinerary-node\">" + cgi.escape(
            edge.to_node
        ) + "</span>.\n" +
        margin + "\t\t</li>\n" +
        # End the nested unordered list.
        margin + "\t</ul>\n" +
        # End the list item.
        margin + "</li>\n"
    )
