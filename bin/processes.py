#!/usr/bin/env python

#
# Checks existence of some processes, when a process does not exist,
# a mail is sent.  The processes.properties file contains the processes 
# and the mail properties.  This properties file must look like:
#
# [processes]
# names = nginx, uwsgi, postgres, django
#
# [mail]
# host = <host>
# port = <port>
# username = <username>
# password = <password>
#

from subprocess import Popen, PIPE
from re import split
from ConfigParser import SafeConfigParser
from os.path import exists

# TODO: get this from the properties file
processes = set(["nginx", "uwsgi", "postgres", "django"])

class Properties():

    def __init__(self, filename):
        parser = SafeConfigParser()
        parser.read(filename)
        self.host = parser.get('mail', 'host')
        self.port = parser.get('mail', 'port')
        self.username = parser.get('mail', 'username')
        self.password = parser.get('mail', 'password')
        # TODO: get properties

class Proc(object):
    '''
        Data structure for a processes. 
        The class properties are process attributes.
    '''
    
    def __init__(self, proc_info):
        self.user = proc_info[0]
        self.pid = proc_info[1]
        self.cpu = proc_info[2]
        self.mem = proc_info[3]
        self.vsz = proc_info[4]
        self.rss = proc_info[5]
        self.tty = proc_info[6]
        self.stat = proc_info[7]
        self.start = proc_info[8]
        self.time = proc_info[9]
        self.cmd = proc_info[10]

    def to_str(self):
        '''
            Returns a string containing minimalistic info
            about the process: user, pid, and command 
        '''
        return '%s %s %s' % (self.user, self.pid, self.cmd)

def get_proc_list():
    '''
        Retrieves a list [] of Proc objects representing the active
        process list list.
    '''

    proc_list = []
    sub_proc = Popen(['ps', 'aux'], shell=False, stdout=PIPE)
    sub_proc.stdout.readline()
    for line in sub_proc.stdout:
        # the separator for splitting is 'variable number of spaces'
        proc_info = split(" *", line.strip())
        proc_list.append(Proc(proc_info))
    return proc_list

def missing_processes():
    """
        Returns missing processes.
    """
    
    proc_list = get_proc_list()
    
    valid = set([])

    for proc in proc_list:
        for check in processes:
            if check in proc.cmd:
                valid.add(check)
    
    return processes - valid
    
def send_mail(host, port, username, password, subject, missing):

    import smtplib
    import string

    FROM = username
    TO = username

    SUBJECT = subject
    
    if len(missing) is 1:
        message = "The " + missing.pop() + " process is missing...\n"
    else:
        message = "Missing these processes:\n"
        for process in missing:
            message += " - " + process + "\n"

    BODY = "Hello,\n" + "\n" + message + "\n" + \
           "Please investigate,\n" + "Your machine"
           
    body = string.join((
        "From: %s" % FROM,
        "To: %s" % TO,
        "Subject: %s" % SUBJECT,
        "",
        BODY), "\r\n")

    server = smtplib.SMTP(host, port)
    #server.set_debuglevel(2)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(FROM, [TO], body)
    server.quit()
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(version="1.0")
    parser.add_argument("--properties", required=True, dest="file", 
                        help="properties file location is required")
    results = parser.parse_args()
    if not exists(results.file):
        print("Given file does not exist: %s - bailing out." % results.file)
    else:
        properties = Properties(results.file)
        missing = missing_processes()
        if not missing:
            print("No issues. Good!")
        else:
            print("Missing process(es), sending a mail...")
            send_mail(properties.host, 
                      properties.port, 
                      properties.username, 
                      properties.password, 
                      "Website offline!", 
                      missing)