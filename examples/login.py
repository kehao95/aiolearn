from context import aiolearn
import getpass
user = aiolearn.User(username='keh13',
                     password=getpass.getpass("input password:"))
semester = aiolearn.Semester(user)
print(user)
