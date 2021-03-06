# Configuring the Web Portal

Also see [doc/RPKI/CA/Configuration][1] for documentation on the
`/etc/rpki.conf` configuration file.

## Creating Users

See [doc/RPKI/CA/UI/GUI/UserModel][2]

## Configuring Apache

In order to use the web portal, Apache must be installed and configured to
serve the application. See [doc/RPKI/CA/UI/GUI/Configuring/Apache][3].

## Error Notifications via Email

If an exception is generated while the web portal is processing a request, by
default will be logged to the apache log file, and an email will be set to
`root@localhost`. If you wish to change where email is sent, you can edit
`/etc/rpki/local_settings.py` and add the following lines:

    
    
    ADMINS = (('YOUR NAME', 'YOUR EMAIL ADDRESS'),)
    

For example,

    
    
    ADMINS = (('Joe User', 'joe@example.com'),)
    

## Cron Jobs

The web portal makes use of some external data sources to display the
validation status of routing entries. Therefore, it is necessary to run some
background jobs periodically to refresh this data. The web portal software
makes use of the `cron` facility present in POSIX operating systems to perform
these tasks.

### Importing Routing Table Snapshot

In order for the web portal to display the validation status of routes covered
by a resource holder's RPKI certificates, it needs a source of the currently
announced global routing table. The web portal includes a script which can
parse the output of the [RouteViews][4] [full snapshot][5] (**warning**: links
to very large file!).

When the software is installed, there will be a `/usr/local/sbin/rpkigui-
import-routes` script that should be invoked periodically. Routeviews.org
updates the snapshot every two hours, so it does not make sense to run it more
frequently than two hours. How often to run it depends on how often the routes
you are interested in are changing.

Create an entry in root's crontab such as

    
    
    30  */2 *   *   *      /usr/local/sbin/rpkigui-import-routes
    

### Importing ROAs

If you want the GUI's "routes" page to see ROAs when you click those buttons,
you will need to run rcynic. see the [instructions for setting up rcynic][6].

This data is imported by the `rcynic-cron` script. If you have not already set
up that cron job, you should do so now. Note that by default, rcynic-cron is
run once an hour. What this means is that the _routes_ view in the GUI will
**not** immediately update as you create/destroy ROAs. You may wish to run
`rcynic-cron` more frequently, or configure `rcynic.conf` to only include the
TAL that is the root of your resources, and run the script more frequently
(perhaps every 2-5 minutes).

If you are running rootd, you may want to run with only your local trust
anchor. In this case, to have the GUI be fairly responsive to changes, you may
want to run the rcynic often. In this case, you may want to look at the value
of **jitter** in rcynic.conf.

### Expiration Checking

The web portal can notify users when it detects that RPKI certificates will
expire in the near future. Run the following script as a cron job, perhaps
once a night:

    
    
    /usr/local/sbin/rpkigui-check-expired
    

By default it will warn of expiration 14 days in advance, but this may be
changed by using the `-t` command line option and specifying how many days in
advance to check.

   [1]: #_.wiki.doc.RPKI.CA.Configuration

   [2]: #_.wiki.doc.RPKI.CA.UI.GUI.UserModel

   [3]: #_.wiki.doc.RPKI.CA.UI.GUI.Configuring.Apache

   [4]: http://www.routeviews.org

   [5]: http://archive.routeviews.org/oix-route-views/oix-full-snapshot-
latest.dat.bz2

   [6]: #_.wiki.doc.RPKI.RP.rcynic

