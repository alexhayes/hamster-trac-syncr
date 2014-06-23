import sys, os, re, argparse, urllib2, urllib, base64
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from hamster import client

TAG_SEARCH = 'trac'
TAG_SYNCD  = '%s-syncd' % TAG_SEARCH
TAG_IGNORE = '%s-ignore' % TAG_SEARCH

_TICKET_PATTERN = ('.{0,}#(?P<ticket>\d+)')
_TICKET_REGEX = re.compile(_TICKET_PATTERN)

def activity_contains_ticket(activity):
    """
    Returns a ticket id if a Hamster activity contains a reference to a ticket.
    """
    match = _TICKET_REGEX.match(activity)
    if not match:
        return False
    return int(match.groupdict()['ticket'])

def reset(start, end, verbose=False):
    """
    Remove all trac-* tags from hamster facts.
    
    Note that this does not remove the time entry from trac and thus should be
    used with caution.
    """
    storage = client.Storage()

    # Retrieve facts (times) from hamster and group time spent into days.
    for fact in storage.get_facts(start, end, "trac"):
        removed = False
        for tag in fact.tags:
            if tag in (TAG_SEARCH, TAG_SYNCD, TAG_IGNORE):
                fact.tags.remove(tag)
                removed = True
        if removed:
            storage.update_fact(fact.id, fact)
            if verbose:
                print "Updating fact '%s'." % fact.activity

def sync(start, end, trac_url, user, password, verbose=False):
    """
    Sync Hamster activities to a Trac project.
    """
    tickets = {}
    storage = client.Storage()
    
    # Retrieve facts (times) from hamster and group time spent into days.
    for fact in storage.get_facts(start, end, TAG_SEARCH, True):
        ticket_id = activity_contains_ticket(fact.activity)
        if not ticket_id:
            fact.tags.append(TAG_IGNORE)
            storage.update_fact(fact.id, fact)
            print "Ignoring activity '%s' on '%s'-'%s' - doesn't reference a ticket." % (fact.activity, fact.start_time, fact.end_time)
            if verbose:
                print "  Updated fact '%s' with tag #trac-ignore" % (fact.id)
            continue
        
        spent = fact.delta.seconds / 60.0 / 60 # get time spent in hours.
        
        if spent == 0:
            fact.tags.append(TAG_IGNORE)
            storage.update_fact(fact.id, fact)
            print "Ignoring activity '%s' on '%s'-'%s' - spent 0 time." % (fact.activity, fact.start_time, fact.end_time)
            if verbose:
                print "  Updated fact '%s' with tag #trac-ignore" % (fact.id)
            continue
        
        if not ticket_id in tickets:
            tickets[ticket_id] = {'activity': fact.activity, 'dates': {}, 'facts': []}
        
        tickets[ticket_id]['facts'].append(fact)
        
        if not fact.start_time.strftime('%Y-%m-%d') in tickets[ticket_id]['dates']:
            tickets[ticket_id]['dates'][fact.start_time.strftime('%Y-%m-%d')] = 0
        
        tickets[ticket_id]['dates'][fact.start_time.strftime('%Y-%m-%d')] += spent
    
    # Now for each ticket create an entry for each day.
    for ticket_id, data in tickets.iteritems():
        for date, spent in data['dates'].iteritems():
            params = urllib.urlencode({
                'ticket_id': ticket_id, 
                'author': user,
                'spent': spent,
                'message': "Hamster activity '''%s''' on ''%s'' by ''%s'' for facts ''%s''." % (data['activity'], date, user, ", ".join([str(fact.id) for fact in data['facts']]))
            })
        
            try:
                request = urllib2.Request("%s/trac-hamster-plugin?%s" % (trac_url, params))
                base64string = base64.encodestring('%s:%s' % (user, password)).replace('\n', '')
                request.add_header("Authorization", "Basic %s" % base64string)   
                result = urllib2.urlopen(request)
                
                if verbose:
                    print "Sync'd activity '%s' on '%s' by '%s'." % (data['activity'], date, user)
                for fact in data['facts']:
                    # Tag facts so that we don't process them again next time the cron runs.
                    fact.tags.append(TAG_SYNCD)
                    storage.update_fact(fact.id, fact)
                    if verbose:
                        print "  Updated fact '%s' with tag #trac-syncd" % (fact.id)
            except urllib2.HTTPError as e:
                print "Failed syncing activity '%s' on '%s' by '%s': %s" % (data['activity'], date, user, e)