#!/usr/bin/env python3

import re
import sys

# sys.arg[0] will have file name
commit_message = " ".join(sys.argv[1:])

commit_flag = re.search(r'\[(.*)\]', commit_message)
if commit_flag:
<<<<<<< HEAD
  print(commit_flag.group(1))
else:
  print("build_all")
=======
  # commit_flag.group(0) : This will give the string along with []
  print(commit_flag.group(1))
else:
  print("build_all")


"""
def extract(s):
    start = s.find('[')
    if start == -1:
        # No opening bracket found. Should this be an error?
        return ''
    start += 1  # skip the bracket, move to the next character
    end = s.find(']', start)
    if end == -1:
        # No closing bracket found after the opening bracket.
        # Should this be an error instead?
        return s[start:]
    else:
        return s[start:end] 
"""
        
>>>>>>> 5d485d00694c99816f6cb6e55a0ec363d587cbf7
