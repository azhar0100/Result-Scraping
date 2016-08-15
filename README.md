Result-Scraping
===============
This program fetches the Lahore board results.

How to use.
-----------

###get_result program
+ Download the program.
+ This program has a lot of dependencies. Download the dependencies using pip,as

    ```
    pip install dependency-name
    // You might need to execute this as root (i.e preceded with sudo) in linux.
    ```

  - Beautiful Soup
  - ConfigArgParse
  - requests
  Install them by

  ```
  pip install bs4 configargparse requests
  ```
+ Invoke it by going to the directory in which you installed it and invoking with
  - On windows

	```
		python.exe get_result.py
	```

  - On UNIX

	```
		./get_result.py
	```
+ The get_result script takes some arguments, the details of which may be obtained by passing `--help` to `get_result.py` as `get_result.py --help`.

+ Look at the progress i guess.

####Note
If the performance is slow , you might want to invoke the program with --pool-size something-more-than-100

###Note
This program may not use the complete internet bandwidth because of CPython GIL, use pypy to bypass that.
