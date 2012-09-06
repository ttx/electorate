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
        self.fullname = None
        self.emails = set()
        self.projects = []
        self.member = None

    def add(self, row, project):
        self.fullname = row[1]
        for email in row[2:]:
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

email_matches = {}
fullname_matches = {}
reorderedname_matches = {}
lastname_matches = {}
missing = {}

for lpid,committer in committers.iteritems():
    # email match
    for email, member in members.iteritems():
        if email in committer.emails:
            email_matches[lpid] = committer
            email_matches[lpid].associate(member)
            break
    else:
        # fullname match
        for email, member in members.iteritems():
            if (committer.fullname == "%s %s" % (
                    member.first_name, member.last_name)):
                fullname_matches[lpid] = committer
                fullname_matches[lpid].associate(member)
                break
        else:
        # reordered name match
            for email, member in members.iteritems():
                if (committer.fullname.find(member.last_name) != -1 and
                    committer.fullname.find(member.first_name) != -1):
                    reorderedname_matches[lpid] = committer
                    reorderedname_matches[lpid].associate(member)
                    break
            else:
                # Last name only match
                for email, member in members.iteritems():
                    if (committer.fullname.find(member.last_name) != -1):
                        lastname_matches[lpid] = committer
                        lastname_matches[lpid].associate(member)
                        break
                else:
                    # Add to missing
                    missing[lpid] = committer

print "== Email matches =="
for lpid, committer in email_matches.iteritems():
    print "%s %s" % (lpid, committer.member.email)
print
print "== Full name matches =="
for lpid, committer in fullname_matches.iteritems():
    print "%s %s %s" % (lpid, committer.member.email, committer.emails)
print
print "== Reordered name matches =="
for lpid, committer in reorderedname_matches.iteritems():
    print "%s %s [%s %s = %s]" % (
        lpid, committer.member.email, committer.member.first_name,
        committer.member.last_name, committer.fullname)
print
print "== Last name matches =="
for lpid, committer in lastname_matches.iteritems():
    print "%s %s [%s %s = %s ?]" % (
        lpid, committer.member.email, committer.member.first_name,
        committer.member.last_name, committer.fullname)
print
print "== Missing matches =="
for lpid, committer in missing.iteritems():
    print "%s %s %s" % (
        lpid, committer.fullname, list(committer.emails))
