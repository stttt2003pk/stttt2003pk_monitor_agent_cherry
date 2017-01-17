Installation

Update and install some dependencies:

yum -y update
yum install -y httpd net-snmp perl pycairo mod_wsgi python-devel git gcc-c++ pytz
Add the EPEL repo from:

http://www.unixmen.com/install-epel-repository-centos-rhel-7/
Install Python Package manager:

yum install -y python-pip node npm
I have installed the graphite within pip,
pip install pytz

pip install 'django<1.6'
pip install 'Twisted<12'
pip install 'django-tagging<0.4'
pip install whisper
pip install graphite-web
pip install carbon

yum install collectd collectd-snmp
git clone https://github.com/etsy/statsd.git /usr/local/src/statsd/

Configuration

Please make these configurations:

cp /opt/graphite/examples/example-graphite-vhost.conf /etc/httpd/conf.d/graphite.conf
cp /opt/graphite/conf/storage-schemas.conf.example /opt/graphite/conf/storage-schemas.conf
cp /opt/graphite/conf/storage-aggregation.conf.example /opt/graphite/conf/storage-aggregation.conf
cp /opt/graphite/conf/graphite.wsgi.example /opt/graphite/conf/graphite.wsgi
cp /opt/graphite/conf/graphTemplates.conf.example /opt/graphite/conf/graphTemplates.conf
cp /opt/graphite/conf/carbon.conf.example /opt/graphite/conf/carbon.conf
chown -R apache:apache /opt/graphite/storage/
vi /opt/graphite/conf/storage-schemas.conf
[default]
pattern = .*
retentions = 10s:4h, 1m:3d, 5m:8d, 15m:32d, 1h:1y

Create a super-user in graphite to save your graphs.

cd /opt/graphite/webapp/graphite
sudo python manage.py syncdb

Getting Started

systemctl enable httpd
systemctl start httpd
/opt/graphite/bin/carbon-cache.py start
You can run the graphite  server:
/opt/graphite/bin/run-graphite-devel-server.py /opt/graphite/





#wsgi apache deployment
#remember to check the error log and find out the permission bug
#remember to create the db not using root, because your apache always not running at root.if you restore the db again,you should try to restart the apache server
#remember to pip intall pytz
#remember to change the permision for apache to access the python lib

# This needs to be in your server's config somewhere, probably
# the main httpd.conf
#listen 8080
NameVirtualHost *:80
# This line also needs to be in your server's config.
# LoadModule wsgi_module modules/mod_wsgi.so

# You need to manually edit this file to fit your needs.
# This configuration assumes the default installation prefix
# of /opt/graphite/, if you installed graphite somewhere else
# you will need to change all the occurances of /opt/graphite/
# in this file to your chosen install location.

<IfModule !wsgi_module.c>
    LoadModule wsgi_module modules/mod_wsgi.so
</IfModule>

# XXX You need to set this up!
# Read http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGISocketPrefix
WSGISocketPrefix run/wsgi

<VirtualHost *:80>
        ServerName 192.168.204.239
        DocumentRoot "/opt/graphite/webapp"
        ErrorLog /opt/graphite/storage/log/webapp/error.log
        CustomLog /opt/graphite/storage/log/webapp/access.log common

        # I've found that an equal number of processes & threads tends
        # to show the best performance for Graphite (ymmv).
        WSGIDaemonProcess graphite processes=5 threads=5 display-name='%{GROUP}' inactivity-timeout=120
        WSGIProcessGroup graphite
        WSGIApplicationGroup %{GLOBAL}
        WSGIImportScript /opt/graphite/conf/graphite.wsgi process-group=graphite application-group=%{GLOBAL}

        # XXX You will need to create this file! There is a graphite.wsgi.example
        # file in this directory that you can safely use, just copy it to graphite.wgsi
        WSGIScriptAlias / /opt/graphite/conf/graphite.wsgi 

        # XXX To serve static files, either:
        # django-admin.py collectstatic --noinput --settings=graphite.settings
        # * Install the whitenoise Python package (pip install whitenoise)
        # or
        # * Collect static files in a directory by running:
        #     django-admin.py collectstatic --noinput --settings=graphite.settings
        #   And set an alias to serve static files with Apache:
        Alias /content/ /opt/graphite/webapp/content/
        <Location "/content/">
                SetHandler None
        </Location>

        # XXX In order for the django admin site media to work you
        # must change @DJANGO_ROOT@ to be the path to your django
        # installation, which is probably something like:
        # /usr/lib/python2.6/site-packages/django
        Alias /media/ "@DJANGO_ROOT@/contrib/admin/media/"
        <Location "/media/">
                SetHandler None
        </Location>

        # The graphite.wsgi file has to be accessible by apache. It won't
        # be visible to clients because of the DocumentRoot though.
        <Directory /opt/graphite/conf/>
                #Order deny,allow
                #Allow from all
                Require all granted
        </Directory>
        <Directory /opt/graphite/webapp>
                #Order deny,allow
                #Allow from all
                Require all granted
        </Directory>

        <Directory /usr/lib/python2.7/site-packages/>
                #Order deny,allow
                #Allow from all
                Require all granted
        </Directory>
</VirtualHost>
