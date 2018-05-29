#! python2
#File: settings.py


# Subject settings.

subject_id = 'DUMMY_1'



# File-transfer settings.

# Numbered sets of parameters for easy use of the script in different contexts.
config_sets = {
           1: [1],
           }

# Numbered sets of parameters for easy use of the script in different contexts.
configs = {
           1: ['down', 'Lifelogging', 'no', 'yes', 'yes'],
           }

# Location of the transfer folder in each context.
paths = {
            'up': {
                   'Lifelogging': 'E:\\VIDEO\\',
                   },
            'down': {
                     'Lifelogging': 'D:\\Lifelogging_data\\',
                     },
            }

# Lists of folders to skip in each context.
skip_array = {
             'up': {
                    'Lifelogging': [],
                    },
             'down': {
                      'Lifelogging': [],
                      }
             }

# Lists of folders to exclusively target in each context.
target_array = {
             'up': {
                    'Lifelogging': [],
                    },
             'down': {
                      'Lifelogging': [],
                      }
             }
