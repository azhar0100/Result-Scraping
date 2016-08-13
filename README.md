Result-Scraping
===============
This program fetches the Lahore board results.

How to use.
-----------

###get_result program
+ Download the program.
+ Download the dependencies
  - Beautiful Soup
  - ConfigArgParse
  - requests
+ Invoke it by going to the directory in which you installed it and invoking with
  - On windows

```
python.exe get_result.py
```

  -On UNIX

```
./get_result.py
```

+ Look at the progress i guess.

####Note
If the performance is slow , you might want to invoke the program with --pool-size something-more-than-100

###Note
This program may not use the complete internet bandwidth because of CPython GIL, use pypy to bypass that.
