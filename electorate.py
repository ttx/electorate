import csv
import os
import sys
import StringIO

if len(sys.argv) < 2:
    print "Usage: %s membersfile commitfile ..." % sys.argv[0]
    sys.exit(1)

membersfile = sys.argv[1]
committersfiles = sys.argv[2:]

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

missing = {}
pure_output = StringIO.StringIO()
impure_output = StringIO.StringIO()

for lpid,committer in committers.iteritems():
    email_matches = []
    fullname_matches = []
    reorderedname_matches = []
    lastname_matches = []
    match_found = False

    for email, member in members.iteritems():
        # email matches
        if email in committer.emails:
            email_matches.append(member)
        # full name matches
        if (committer.fullname == "%s %s" % (
                member.first_name, member.last_name)):
            fullname_matches.append(member)
        # reordered name match
        if (committer.fullname.find(member.last_name) != -1 and
                committer.fullname.find(member.first_name) != -1):
            reorderedname_matches.append(member)
        # Last name only match
        if (committer.fullname.find(member.last_name) != -1):
            lastname_matches.append(member)

    prefix= "%s (%s)" % (lpid, committer.fullname)
    if len(email_matches) == 1:
        print >>pure_output, "%s %s [email match]" % (
                              prefix, email_matches[0].email)
        continue
    if len(email_matches) > 1:
        print >>impure_output, "%s [DUPLICATE email matches:" % prefix,
        for member in email_matches:
            print >>impure_output, member.email,
        print >>impure_output, "]"
        continue
    if len(fullname_matches) == 1:
        print >>pure_output, "%s %s [fullname match]" % (
                              prefix, fullname_matches[0].email)
        continue
    if len(fullname_matches) > 1:
        print >>impure_output, "%s [DUPLICATE fullname matches:" % prefix,
        for member in fullname_matches:
            print >>impure_output, member.email,
        print >>impure_output, "]"
        continue
    if reorderedname_matches or lastname_matches:
        print >>impure_output, "%s [FUZZY matches with:" % prefix,
        for member in reorderedname_matches + lastname_matches:
            print >>impure_output, "%s %s (%s)," % (
                         member.first_name, member.last_name, member.email),
        print >>impure_output, "]"
        continue
    print >>impure_output, "%s MISSING, apparently not a member" % prefix
print "PURE matches:"
print pure_output.getvalue()
print
print "IMPURE matches:"
print impure_output.getvalue()
