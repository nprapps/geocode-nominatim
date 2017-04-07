geocode-nominatim
=================

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [What's in here?](#whats-in-here)
* [Bootstrap the project](#bootstrap-the-project)
* [Geocode unstructured data](#geocode-unstructured-data)
* [Geocode structured data](#geocode-structured-data)
* [Geocode mixed data](#geocode-mixed-data)
* [Advanced configuration](#advanced-configuration)

What is this?
-------------

Geocode addresses using [Nominatim geocode service](https://wiki.openstreetmap.org/wiki/Nominatim).

It uses a simple cache file to optimize the need for redundant geolocation.

If you plan to do a **big** geocoding batch, please contact [Nominatim geocode service](https://wiki.openstreetmap.org/wiki/Nominatim) to let them know that you are planning to do so. They will point you to the right time to execute or give you some recommendations over what frequency to use, etc.

Assumptions
-----------

The following things are assumed to be true in this documentation.
* You are running OSX.
* You are using Python 2.7. (Probably the version that came OSX.)
* You have virtualenv and virtualenvwrapper installed and working.
* You have postgres installed and running

For more details on the technology stack used with the app-template, see our [development environment blog post](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html).

This code should work fine in most recent versions of Linux, but package installation and system dependencies may vary.

What's in here?
---------------

The project contains the following folders and important files:

* ``code`` -- Where are lambda function code lives
* ``test``-- test csv files with some examples of allowed formats
* ``geocode.py`` -- Main Python script
* ``requirements.txt`` -- Python requirements.

Bootstrap the project
---------------------

To bootstrap the project:

```
git clone git@github.com:nprapps/geocode-nominatim.git
cd geocode-nominatim
mkvirtualenv geocode-nominatim
pip install -r requirements.txt
```

Geocode unstructured data
-------------------------

In order to geocode an unstructured address, create a csv file with the following headers:
* address -- unstructured format, wrap in quotes if it contains commas

```
$python geocode.py $CSVFILE
```

_Where $CSVFILE is the path to the csv file on your hard drive_

The results will be stored in the `output` folder

Geocode structured data
-----------------------

In order to geocode an unstructure address, create a csv file with the following headers:
* street -- \[street number\] \[steetname\]
* city
* state
* country
* postalcode

Fill one or as many as the fields as you need to specify the location that you want to geocode. Then run the script

```
$python geocode.py $CSVFILE
```

_Where $CSVFILE is the path to the csv file on your hard drive_

The results will be stored in the `output` folder

Geocode mixed data
------------------

If you have a mix of unstructured and structured location then create a csv file with the following headers:
* address -- use this for the unstructured locations
* street -- \[street number\] \[steetname\] for structured locations
* city -- for structured locations
* state -- for structured locations
* country -- for structured locations
* postalcode -- for structured locations

Fill either the `address` for the unstructured locations and one or as many as the fields as you need to specify the location that you want to geocode for structured locations. Then run the script

```
$python geocode.py $CSVFILE
```

_Where $CSVFILE is the path to the csv file on your hard drive_

The results will be stored in the `output` folder

Advanced Configuration
----------------------

The `geocode.py` scripts can be customized with some advanced behaviors

### Debugging

You can add a debug flag to the script to have a more verbose execution

```
$python geocode.py $CSVFILE -d
```

### Sample

If you want to test the execution on a sample of the data prior to launching the full dataset then:

```
$python geocode.py $CSVFILE -s $SAMPLE_SIZE
```

_Where $SAMPLE_SIZE is the number of lines to be used for the sample from the beginning of the csv_

### No Cache

The script uses a file based cache to optimize the number of requests to the Nominatim service.

If you do not want to use the file cache at all add the no-cache flag like this:

```
$python geocode.py $CSVFILE -C
```

### Wait between geocoding executions

You can customize the number of seconds to wait between consecutive executions of the geocoding service:

```
$python geocode.py $CSVFILE -w $WAIT_SECONDS
```

_Where $WAIT_SECONDS is the number of seconds to wait until the next execution_
