import os
import datetime
import glob


def delete_files_older_than(path, days):
    today = datetime.datetime.today()  # gets current time
    os.chdir(path)  # changing path to current path(same as cd command)

    # we are taking current folder, directory and files
    # separetly using os.walk function
    for root, directories, files in os.walk(path, topdown=False):
        for name in files:
            # this is the last modified time
            t = os.stat(os.path.join(root, name))[8]
            filetime = datetime.datetime.fromtimestamp(t) - today
            # Delete files older than specified days
            if filetime.days >= days:
                print(os.path.join(root, name), filetime.days)
                os.remove(os.path.join(root, name))
