# test3270
Overview
-----------
IBM z/OS ISPF applications testing framework. It can be used to test TSO/ISPF applications through a TN3270 connection.

Example
-----------
The following example test script uses the TN3270 terminal module in order to connect to a mainframe, pass authorization, invoke DSLIST utility and print screen content. It also shows the capability of this utlity to automatically invoke SDSF from ISPF Primary Option Menu in order to purge the terminal job before disconnection.
```py
from terminal import *

enterString('3.4')
enter()
print(readContent())
executePF(3)
executePF(3)
```
The following shell command can be used to run the above test script:
```text
$ python test.py -s"server address" -u"TSO username" -p"TSO password"
```

