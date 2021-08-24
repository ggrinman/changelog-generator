#!/usr/bin/env python3

# -----------------------------------------------------------
# Creates a Change Log file based on the commits submitted by the developers.
# 
# Angular Convention Types:
# build: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
# ci: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
# docs: Documentation only changes => NOT USED HERE TO PREVENT AUTO GENERATED COMMENTS FOR DOCS
# feat: A new feature
# fix: A bug fix
# perf: A code change that improves performance
# refactor: A code change that neither fixes a bug nor adds a feature
# style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
# test: Adding missing tests or correcting existing tests
# 
# References:
# https://www.conventionalcommits.org/en/v1.0.0/
# https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines
# -----------------------------------------------------------

import re
import shlex
import subprocess
import datetime

def get_commit_log():
    # git log format options https://git-scm.com/docs/git-log
    output = subprocess.check_output(shlex.split('git log --format="%at|**|%s|**|%h" --color'), stderr=subprocess.STDOUT)
    output = output.decode('ascii')
    output = output.split('\n')
    return output

# filter only meaningful commits following the convention
def strip_comment(comment):
    if re.findall(r'^(build:|ci:|feat:|fix:|perf:|refactor:|style:|test:)', comment):
        return comment
    return ''

def group_commits_by_date_and_type(commits):
    output = {}
    for line in commits:
        line_details = line.split('|**|')
        if len(line_details) == 3:
            comment = line_details[1]
            timestamp = line_details[0]
            date = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d')
            dt = datetime.datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
            hash = line_details[2]
            if (strip_comment(comment) != ''):
                if date not in output:
                    output[date] = {}
                type = comment.split(':')[0] + ':'
                if type not in output[date]:
                    output[date][type] = []
                output[date][type].append({"message":comment,"hash":hash,"datetime":dt})
    return output

def overwrite_changelog(commits):
    output = ['# Changelog']
    convention_types = {
        "feat:": "Features",
        "fix:": "Fixes",
        "build:": "Build",
        "ci:": "CI",
        "perf:": "Performance",
        "refactor:": "Refactor",
        "style:": "Styles",
        "test:": "Tests" 
    }
    for date in commits:
        output.append('## ' + date)
        for type in convention_types:
            if type in commits[date]:
                output.append('### ' + convention_types[type])
                for commit in commits[date][type]:
                    output.append('* ' + commit['message'] + ' ([' + commit['hash'] + '](../../commit/' + commit['hash'] + '))')
    # for line in output:
    #     print(line)
    with open("/github/home/CHANGELOG.md", "w+") as file:
        file.writelines("%s\n" % l for l in output)
    return

def main():
    commits = get_commit_log()
    commits = group_commits_by_date_and_type(commits)
    overwrite_changelog(commits)

main()
