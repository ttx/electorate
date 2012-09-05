import csv
import os
import sys

if len(sys.argv) < 3:
    print "Usage: %s [csv|names|emails|missing] membersfile commitfile ..." % sys.argv[0]
    sys.exit(1)

action = sys.argv[1]
membersfile = sys.argv[2]
committersfiles = sys.argv[3:]

class Member(object):
    def __init__(self, row):
        self.first_name = row[0]
        self.last_name = row[1]
        self.email = row[2]

class Committer(object):
    def __init__(self):
        self.emails = set()
        self.projects = []
        self.member = None

    def add(self, row, project):
        for email in row[1:]:
            self.emails.add(email)
        self.projects.append(project)

    def associate(self, member):
        self.member = member

committers = {}
for committersfile in committersfiles:
    project = os.path.basename(committersfile)[:-4]
    with open(committersfile, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] not in committers:
                committers[row[0]] = Committer()
            committers[row[0]].add(row, project)

members = {}
with open(membersfile, 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        members[row[2]]=Member(row)

voters = {}
missing = {}
for lpid,committer in committers.iteritems():
    for email in committer.emails:
        if email in members:
            voters[lpid] = committer
            voters[lpid].associate(members[email])
            break
    else:
        missing[lpid] = committer

if action == 'csv':
    writer = csv.writer(sys.stdout)
    for lpid, committer in voters.iteritems():
        row = [lpid, committer.member.email]
        row.extend(committer.projects)
        writer.writerow(row)

if action == 'names':
    for lpid, committer in voters.iteritems():
        print "%s %s (%s)" % (committer.member.first_name,
                              committer.member.last_name, lpid)

if action == 'emails':
    for lpid, committer in voters.iteritems():
        print committer.member.email

if action == 'missing':
    for lpid, committer in missing.iteritems():
        print lpid, list(committer.emails), committer.projects
