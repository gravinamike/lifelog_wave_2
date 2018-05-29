#! python2
#File: transfer.py

import os
import sys
import shutil
import errno
import stat

from send2trash import send2trash

import settings


def transfer_stick(direction=None, location=None, duplicate='yes',
                   overwrite='no', permadelete='no', configuration=None):
    # Downloads or uploads from one set of directories to another.

    direction_names = ['up', 'down']
    opposite_direction_names = {'up': 'down', 'down': 'up'}

    # Try different approaches to getting all 4 parameters.
    while not (
                direction in direction_names
                and location in ['Lifelogging']
                and duplicate in ['yes', 'no']
                and overwrite in ['yes', 'no']
                and permadelete in ['yes', 'no']
                ):

        # If configuration was not specified,
        if configuration == None:
            # Try to get configuration from user to specify parameters.
            configuration = input('Configuration? (1 - 6): ')
            try:
                configuration = int(configuration)
            except ValueError:
                configuration = None

        if configuration in settings.configs.keys():
            direction, location, duplicate, overwrite, permadelete = settings.configs[configuration]

        # If no valid configuration, ask user for parameters one at a time.
        else:
            print 'direction =', direction, ', location =', location, ', duplicate =', duplicate, 'overwrite =', overwrite, 'delete =', delete
            print 'Parameters not all entered correctly when script called and no valid configuration selected.'
            direction = input('Enter direction (up or down): ')
            location = input('Enter location (home or work): ')
            duplicate = input('Enter whether to duplicate (yes or no): ')
            overwrite = input('Enter overwrite permission (yes or no): ')
            permadelete = input('Enter whether to permadelete old files (yes or no): ')

    # Construct a list of directories for transfer.
    directories = {
                   direction_name: [settings.paths[direction_name][location]]
                   for direction_name in direction_names
                   }
    print ''
    print 'Directories to copy: '
    print directories

    # Get a list of directories to skip transferring, or to target exclusively from parent folder.
    skiplist = settings.skip_array[direction][location]
    targetlist = settings.target_array[opposite_direction_names[direction]][location]
    print ''
    print 'Items to skip: '
    print skiplist
    print ''
    print 'Items to target exclusively from parent folder: '
    print targetlist


    # Transfer the files.
    print ''
    print "Downloading..." if direction == 'down' else "Uploading..."

    for i, directory in enumerate(directories[opposite_direction_names[direction]]):
        transfer_tree(
                      dir_src=directory,
                      dir_dst=directories[direction][i],
                      skiplist=skiplist,
                      targetlist=targetlist,
                      overwrite=overwrite,
                      duplicate=duplicate,
                      permadelete=permadelete,
                      )

    print ''
    print "Transfer complete."



def handleRemoveReadonly(func, path, exc):
    # Handles readonly errors by setting files to readable.
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        raise



class ProgressCount:
    # Tracks progress of a process operating over a list.

    def __init__(self, listlength, milestonesize = 25):
        self.listlength = listlength
        self.milestonesize = milestonesize
        self.progress = 0
        self.milestone = 0

    def increment(self):
        self.progress += 1
        progress_percent = (self.progress / self.listlength) * 100
        if progress_percent >= self.milestone:
            if progress_percent < 100:
                print round(progress_percent), '% ... '
            else:
                print '100%'
            self.milestone = self.milestone + self.milestonesize



def transfer_tree(dir_src, dir_dst, skiplist=[], targetlist=[], overwrite='no',
                  duplicate='no', permadelete='no', symlinks=False, ignore=None):
    # Transfers tree and files from dir_src to dir_dst.

    # Initialize progress trackers.
    counter_copy = ProgressCount(len(os.listdir(dir_src)))
    counter_delete = ProgressCount(len(os.listdir(dir_src)))

	# Checks for duplicate files and folders at destination. If such exist,
    # checks overwrite variable and either deletes originals in prep for
    # overwrite or aborts.
    print ''
    print 'Checking', dir_dst, 'for duplicate files and folders...'

    # Construct a list of duplicate paths.
    deletelist = []
    for item in os.listdir(dir_src):
        s = os.path.join(dir_src, item)
        d = os.path.join(dir_dst, item)
	if (
                   ((len(targetlist) != 0) and not (s in targetlist))
                   or
                   (s in skiplist)
                   or
                   (not os.path.exists(d))
               ):
           pass
        else:
            deletelist.append(d)

    # Either delete the duplicates or report skip.
    if len(deletelist) > 0:
        if overwrite == 'yes':
            print 'File or folder exists at destination and overwrite set to True.'
            print ('Deleting' if permadelete=='no' else 'Permadeleting'), len(deletelist), 'files and/or folders.'
            counter_overwrite = ProgressCount(len(deletelist))
            for item in deletelist:
		if permadelete == 'yes':
                    if os.path.isdir(item):
                        shutil.rmtree(item, ignore_errors=False, onerror=handleRemoveReadonly)
                    else:
                        os.remove(item)
                else:
		    send2trash(item)
                counter_overwrite.increment()
        else:
            print 'File or folder exists at destination and overwrite set to False.'
            print 'Transfer aborted.'
            sys.exit()

    # Copy files over to destination.
    print ''
    print 'Copying', dir_src, 'to', dir_dst

    for item in os.listdir(dir_src):
        s = os.path.join(dir_src, item)
        d = os.path.join(dir_dst, item)
        if (
                    ((len(targetlist) != 0) and not (s in targetlist))
                    or
                    (s in skiplist)
               ):
            pass
        else:
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
        counter_copy.increment()

    # Delete source files.
    if duplicate == 'no':
        print ''
        print ("Deleting original..." if permadelete=='no' else "Permadeleting original...")

        for item in os.listdir(dir_src):
            s = os.path.join(dir_src, item)
            if (
                        ((len(targetlist) != 0) and not (s in targetlist))
                        or
                        (s in skiplist)
                   ):
                pass
            else:
                if permadelete == 'yes':
                    if os.path.isdir(s):
                        shutil.rmtree(s, ignore_errors=False, onerror=handleRemoveReadonly)
                    else:
                        os.remove(s)
                else:
                    send2trash(s)
            counter_delete.increment()
