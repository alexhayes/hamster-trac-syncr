# Hamster to Trac Sync

Sync's activities created in Hamster to Trac tickets.

When creating a activity entry in Hamster you link it to a ticket by putting a 
hash (#) followed by the ticket id. For example, if you are working on a Trac 
ticket with id 451 the following would all map the Hamster activity to the Trac
ticket.

- #451
- #451 My task
- #451@Category My task

Time entries that are not prefixed with a # will not be sync'd to trac.

When a successful sync occurs the activity in Hamster is tagged with 'trac-syncd' to ensure it is created only once in Trac.

# Requirements

On Ubuntu:

	sudo apt-get install libglib2.0-dev gnome-doc-utils vala-dbus-binding-tool gnome-control-center-dev python-distutils-extra intltool python-dateutil
	sudo ln -s /usr/bin/vala-dbus-binding-tool /usr/bin/dbus-binding-tool

## TracHamsterPlugin

You'll need a working trac installation with [Timing and Estimation plugin](http://trac-hacks.org/wiki/TimingAndEstimationPlugin) setup and operational.

Once you've done this you'll then need to install [TracHamsterPlugin](https://github.com/alexhayes/trac-hamster-plugin).

## Hamster

Until an outcome on [this pull request](https://github.com/projecthamster/hamster/pull/167) you will also need to run alexhayes' fork of hamster, this can be installed as follows:

	git clone git://github.com/alexhayes/hamster.git
	cd hamster
	./waf configure build
	sudo ./waf install

If you're already running hamster its possible you will need to do the following:

	sudo apt-get remove hamster-indicator hamster-applet
	
or, if you've previously installed hamster from source:

	git checkout d140d45f105d4ca07d4e33bcec1fae30143959fe
	./waf configure build
	sudo ./waf uninstall
	git checkout master

# Installation

	git clone git@git.roi.com.au:hamster-trac-syncr
	cd hamster-trac-syncr
	sudo python setup.py install

You should now have `hamster-syncr` in your path, to test this you can do the following;

	hamster-syncr -h

Congratulations, you have installed the client.

# Sync

Once installed you can run the following to sync your times to trac.

	hamster-syncr http://example.com/trac/projectx trac-username trac-password

By default, all activity up to the previous day is syncd - run with --help to 
discover other options that can be specified.

# Cron

If you are planning on setting up a cronjob to call the hamster-syncr program you
need to create a bash script similar to the following:

	#!/bin/bash
	
	# Find a DBUS_SESSION_BUS_ADDRESS
	if [[ -z "$DBUS_SESSION_BUS_ADDRESS" ]]; then
		# Get DBUS_SESSION_BUS_ADDRESS if anything knows about it
		WC=$(pgrep notification-)
		[[ -z "$WC" ]] && WC='*'
		export DBUS_SESSION_BUS_ADDRESS="$(
			grep --color=never -ao -m1 -h -P\
			'(?<=DBUS_SESSION_BUS_ADDRESS=).*?\0'\
			/proc/$WC/environ 2>/dev/null | head -1
		)"
	fi
	export DISPLAY=:0
	/usr/local/bin/hamster-syncr --verbose http://example.com/trac/projectx trac-user trac-password

Chmod the script;

	chmod 600 /path/to/hamster-syncr-cron.sh

And in your crontab:

	SHELL=/bin/bash
	* 13 * * * /path/to/hamster-syncr-cron.sh

# Author

Alex Hayes <alex@alution.com> - special thanks to roi.com.au for sponsoring this development
