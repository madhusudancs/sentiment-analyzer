Sentiment Analyzer
==================

The goal of this project is to perform sentiment analysis on textual data that
people generally post on websites like social networks and movie review sites.
At the moment, this project does a sentiment analysis on tweets
(from twitter.com). It has two modes of operation

  * Offline mode: This mode relies on the discoproject (http://discoproject.org/),
    which is a MapReduce framework written in Erlang and Python and has a cool
    Python API. This mode can be used to fetch a large number of tweets using
    the Twitter Search API and to feature extract and classify them.
  * Online mode: Online mode has a Web UI written in Django. This mode can fetch
    only a thousand tweets for one request and classify them.


Technologies used and dependencies
----------------------------------

You should never use Python without **IPython**!!! Although nothing in this
project directly uses IPython or its API, it is highly recommended to install
**IPython** 0.12 or later to make your life easier :-)

The following technologies/packages/libraries are used and hence required::

Base Requirements
~~~~~~~~~~~~~~~~~

  * The project is written in **Python**! So Python 2.7 is the bare minimum
    requirement. Note this project uses several features of Python 2.7 to
    make sure that the transition to Python 3.x will be smooth. So it is
    intentionally written not to support the previous versions of Python.
    Once the dependent libraries like Django are packages are ported to
    Python 3.x this project should theoritically run on Python 3.x, but it
    has not been tested as of now.
  * The classifier is implemented using **Scikit-Learn** (sklearn) library which
    is a Python machine learning library written on top of Python for Scientific
    Computing stack. So Scikit-Learn is required. This project runs only on
    the current bleeding edge version of Scikit-Learn. You need to git clone
    Scikit-Learn's repository from their github page and install it from there.
    The project uses some API that are not available in previous versions. So
    only Scikit-Learn 0.11+ works.
  * Since Scikit-Learn depends on Python for Scientific Computing stack.
    **NumPy** and **SciPy** which are the foundations of this stack are required.
  * Data persistence is achieved using **MongoDB**. So **MongoDB** v2.0.3 or
    later is required.
  * **MongoEngine** which is a Python API for MongoDB is used to make the Python
    components talk to MongoDB. So **MongoEngine** 0.6.2 or later is required.
  * **requests** library which is an awesome library for all HTTP related
    things in Python is used for fetching tweets through the Twitter Search API.
    So **requests** 0.10.4 is required.

MapReduce/Offline mode requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  * Discoproject needs to be installed for this mode. This needs the bleeding
    edge version of discoproject. So discoproject needs to be installed from
    their github repository.


Web UI/Online mode requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  * The WebUI is implemented using **Django**. But we use MongoDB as our data
    backend which is a NoSQL. Django still doesn't officially support any NoSQLs.
    So the thirdparty Django fork called **Django-nonrel** is required. The
    version of Django-nonrel that works with **Django** 1.3 or later is
    required for this mode.
  * For making Django components talk to MongoDB backend, **djangotoolbox** and
    **Django MondoDB Engine** are required. These can be any recent versions
    from their respective bitbucket and github repositories.
  * Additionally caching is supported for classified tweets in order to speedup
    the request-to-response cycle. This is implemented using **Memcached**. So
    **Memcached** 1.4.7 or later is required.
  * The Python API for Memcached **PyLibMC** is used to make Python components
    talk to Memcached backend. Bleeding edge of **PyLibMC** is used so, this
    needs to be git-cloned from their github repository.
  * **django-mongonaut** is used to provide Django admin like functionality on
    top of MongoDB. So **django-mongonaut** 0.2.11 or later is required.


Setting up
----------

The steps to setup this project are

  * First of all, to get this code locally, git-clone this repository. The git
    clone URL is at the front page of this project.
  * Then make sure the package requirements as mentioned in the requirements
    section above are met.
  * You will need to create a Python file called **datasettings.py** in the project
    root directory. This file contains all the project specific settings that
    are local to your machine. The sample datasettings file is provided in the
    project root directory. If you want to reuse it just copy it to a new file
    and name it **datasettings.py**
  * For both modes of operation, the MongoDB database to connect to is defined
    in webui/fatninja/models.py with the line::

        mongoengine.connect('<database name>')

    Replace the <> place holder with your database name. **This is required for
    MapReduce/Offline mode too since we write the data to database even during
    MapReduce.**

  * For running in Web UI/online mode you will also need **local.py** in the
    webui directory under project root. This file contains information either
    some sensitive information like the database name, password etc. A sample
    is provided. You can just copy it to a new file and call it **local.py**
    and replace all the placeholders shown by angular brackets (<>) with
    information specific to your machine.


What was the training data used and what else is required?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to create a data directory and point the settings variable 
**DATA_DIRECTORY** in your datasettings.py file to point to that location.
Then you will need the training corpus. The training corpus used can be
obtained from here::

  http://www.sananalytics.com/lab/twitter-sentiment/

Build a training corpus out of it this data as a CSV file and name it
**full-corpus.csv**. Place this CSV file under your data directory.

Additionally IMDB reviews classification was tried for training but it did not
improve precision values in any way. So it was discared. If you are interested
to experiment you can get that data from here::

  http://alias-i.com/lingpipe/demos/tutorial/sentiment/read-me.html

These files can be directly placed under directories **positive** and
**negative** under your data directory and the IMDB data parser in **parser.py**
can be used to parse this data and fed into the classifier while training it.
But this is left as an exercise :-)

Training the classifiers
~~~~~~~~~~~~~~~~~~~~~~~~

Only the **First Time**, to train the classifiers and store the vectorizer and
the trained classifier navigate to analyzer directory and run::

    python train.py --serialize

Assuming you have setup everything else, this trains 3 classifiers

    * A Multinomial Naive-Bayes classifier
    * A Bernoulli's Naive-Bayes classifier
    * A Support-Vector Machine

and stores the trained classifiers in the given order in the serialized file
called **classifiers.pickle** in your data directory:

This also stores the vectorizer object in the file **vectorizer.pickle** in your
data directory.

    
Enough is enough, tell me how to run?
-------------------------------------

Ok finally! To run in the MapReduce/Offline mode navigate to analyzer directory
and run::

    $ python classification.py -q "Oscars" -p 10

where the argument to -q is the search query to search for tweets on twitter
and the argument to -p is the number of pages of search results to fetch. Each
page roughly contains 80-100 tweets and this option defaults to 10.

Usage::

    $ python classification.py -h
    usage: classification.py [-h] [-q Query] [-p [Pages]]

    Classifier arguments.

    optional arguments:
      -h, --help            show this help message and exit
      -q Query, --query Query
                            The query that must be used to search for tweets.
      -p [Pages], --pages [Pages]
                            Number of pages of tweets to fetch. One page is
                            approximately 100 tweets.


To run in the Web UI mode all you have to do is start the Django webserver. To
do this navigate to webui directory and run::

    $ python manage.py runserver

You can visit the URL that the Django webserver points to see how it runs.


Why discoproject for MapReduce, why not X?
------------------------------------------

The API of discoproject is much much cleaner, better and easier to use
than Hadoop or any other related MapReduce APIs that we came across. Also,
setting up discoproject is extremely easy. If we are not interested in
installing discoproject, we can even run it from the source directory after
git-cloning it! And it runs on Python! Not in any other X programming language
that is defective-by-design! Also, on a single node cluster, discoproject seems
to run faster than Hadoop at least. However we don't consider this as a win
yet. We need to really profile discoproject and other frameworks on large
clusters with Terabytes of data to know which actually outperforms the other.


AUTHORS
-------

    * Ajay S. Narayan
    * Madhusudan.C.S
    * Shobhit N.S.


LICENSE and COPYRIGHT
---------------------

The authors of this project are the sole copyright holders of the source code
of this project, unless otherwise explicitly mentioned in the individual source
files. The source code includes anything that can be written in any computer
programming or scipting or markup languages.

This is an open source project licensed under Apache License v2.0. The terms
and the conditions of the license is available in the "LICENSE" file.

