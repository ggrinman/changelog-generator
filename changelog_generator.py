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

def get_commit_log():
    # TODO find how to use timestamp instead to sort by datetime and keep items grouped by type
    # git log format options https://git-scm.com/docs/git-log
    output = subprocess.check_output(shlex.split('git log --format="%as|**|%s|**|%h" --color'), stderr=subprocess.STDOUT)
    output = output.decode('ascii')
    output = output.split('\n')
    return output

# filter only meaningful commits following the convention
def strip_comment(comment):
    if re.findall(r'^(build:|ci:|feat:|fix:|perf:|refactor:|style:|test:)', comment):
        return comment
    return ''

def overwrite_changelog_by_date(commits):
    output = ['# Change Log']
    convention_types = {
        "build:": "Build",
        "ci:": "CI",
        "feat:": "Features",
        "fix:": "Fixes",
        "perf:": "Performance",
        "refactor:": "Refactor",
        "style:": "Styles",
        "test:": "Tests" 
    }    
    current_date = ''
    current_type = ''
    for line in commits:
        line_details = line.split('|**|')
        if len(line_details) == 3:
            comments = line_details[1]
            date = line_details[0]
            hash = line_details[2]
            if (strip_comment(comments) != ''):
                if (date != current_date):
                    current_date = date
                    current_type = ''
                    output.append('## ' + date)
                for type in convention_types:
                  if re.findall(r'^' + type, comments) and current_type != convention_types[type]:
                      current_type = convention_types[type]
                      output.append('### ' + current_type)
                # if re.findall(r'^feat:', comments) and current_type != 'Features':
                #     current_type = 'Features'
                #     output.append('### Features')                
                output.append('* ' + comments + ' ([' + hash + '](../../commit/' + hash + '))')
    with open("/github/home/CHANGELOG.md", "w+") as file:
        file.writelines("%s\n" % l for l in output)
    # for line in output:
    #     print(line)
    return

def main():
    commits = get_commit_log()
    overwrite_changelog_by_date(sorted(commits, reverse=True))

main()
