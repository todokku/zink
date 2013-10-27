from fabric.api import run, env
from fabric.decorators import task
from fabric.colors import red, green, yellow
from fabric.operations import require, sudo
from fabric.context_managers import show, settings, cd
from fabric.utils import abort
from fabric.contrib import django

from os.path import join, dirname, realpath

#
# Base configuration first
#

env.project = "zink"
env.repo = "hg.elevenbits.org"
env.prefix = '/var/www'
env.path = "%(prefix)s/%(project)s" % env
env.local = dirname(realpath(join(__file__, "..")))
env.upload = "%(prefix)s/%(project)s/static/upload" % env
env.media = "%(prefix)s/%(project)s/media" % env


#
# Some config utility methods
#


def _create_environment(filename, environment):
    """
        Creates the correct env keys for an environment using a given
        configuration filename.
    """
    from ConfigParser import SafeConfigParser
    from os.path import isfile
    if not isfile(filename):
        print(red("Configuration file '" + filename + "' does not exist."))
        return False
    config = SafeConfigParser()
    config.read(filename)
    if environment in config.sections():
        env.settings = environment
        return _add_properties(config, environment)
    else:
        print(red("Could not find the [" + environment + 
              "] section in '" + filename + "'."))
        return False
    

def _add_properties(config, section):
    """
        Gets the entries of a section from a config parser.
    """
    from ConfigParser import NoOptionError
    try:
        env.user = config.get(section, "user.username")
        env.password = config.get(section, "user.password")
        env.dbuser = config.get(section, "db.username")
        env.dbpassword = config.get(section, "db.password")
        env.dbname = config.get(section, "db.name")
        env.hosts = [config.get(section, "host")]
        return True
    except NoOptionError as noe:
        print(red("Could not find the '" + noe.option + 
              "' key in the '" + noe.section + "' section."))
        return False


#
# The three environments.
#


@task
def production():
    """
        Build for a Production environment.
    """
    _create_environment("fabfile.properties", "production")


@task
def staging():
    """
        Build for a Staging environment.
    """
    _create_environment("fabfile.properties", "staging")


@task
def development():
    """
        Build for a Development environment.
    """
    _create_environment("fabfile.properties", "development")


#
# The tasks
#


@task
def tip():
    """
        Deploy the tip.
    """
    env.branch = 'tip'


@task
def revision(revision="tip"):
    """
        Deploy a certain revision.  Default is the tip.
    """
    env.branch = revision


@task
def deploy():
    """
        Setup a new website by installing everything we need, and fire up 
        the database.  Then start the server.
    """
    
    require('settings', provided_by=[production, staging, development])
    require('branch', provided_by=[tip, revision])

    print(green("Fabricating " + env.branch + " in " +
                env.settings + " environment..."))

    remove_previous_releases()
    create_prefix_directory()

    if env.settings == "development" and env.branch == "tip":
        print(green("Since in development and deploying tip, " +
                    "just symbolically linking..."))
        create_user()
        create_database()
        #link_local_files()
        copy_current()
        create_media_directory()
    else:
        create_root_directory()
        create_media_directory()

        # TODO: make a backup of the staging|production database environment
        # TODO: create a new revision

        print(green("Getting files from repository..."))
        if (env.branch == "tip"):
            checkout_latest()
        else:
            checkout_revision(env.branch)

        install_requirements()

        create_database()
        populate_database()
        restart_database()

        add_cronjob() # checks existence of some core processes

    #create_upload_directory()

    create_uwsgi_upstart()

    update_webserver()
    restart_webserver()

    print(green("Setup complete."))

#
# Tasks to help in deployment
#


def add_cronjob():
    """
        Add a cronjob which checks for the correct processes to be running.
    """
    sudo("cp %(path)s/conf/processes /etc/cron.d/processes" % env)


def remove_previous_releases():
    sudo("rm -rf %(path)s" % env)


def create_prefix_directory():
    sudo("mkdir -p %(prefix)s" % env)


def create_root_directory():
    """
        Create directories necessary for deployment.
    """
    sudo("mkdir -p %(path)s" % env)
    sudo("chown www-data:www-data %(path)s" % env)


def copy_current():
    sudo('cp -r %(local)s %(prefix)s' % env)
    sudo("chown www-data:www-data --recursive %(path)s" % env)


def link_local_files():
    sudo('ln -s %(local)s %(path)s' % env)
    sudo("chown www-data:www-data --recursive %(path)s" % env)


def create_upload_directory():
    """
        Allow write access by group on upload directory
    """
    sudo("mkdir -p %(upload)s" % env)
    sudo("chown www-data:www-data --recursive %(upload)s" % env)
    sudo("chmod 777 %(upload)s" % env)
    sudo("ls -al %(upload)s" % env)


def create_media_directory():
    """
        Create media directory
    """
    sudo("mkdir -p %(media)s" % env)
    sudo("chown www-data:www-data %(media)s" % env)
    sudo("chmod 777 %(media)s" % env)
    sudo("ls -al %(media)s" % env)


def checkout_latest():
    """
        Get latest version from repository.
    """
    sudo('hg clone https://%(user)s:%(password)s@%(repo)s/%(project)s %(path)s' % env, user="www-data")


def checkout_revision(revision):
    """
        Clone a revision.
    """
    sudo('hg clone -r %(branch)s https://%(user)s:%(password)s@%(repo)s/%(project)s %(path)s' % env, user="www-data")


def install_requirements():
    """
        Install the required packages using pip.
    """
    sudo('pip install -r %(path)s/requirements.txt' % env)
    print(green("Some required packages are installed."))
    print(yellow("Some packages might be missing."))
    print(yellow("You still need to do check this yourself for now..."))


@task
def backup():
    """
        Dump the latest content of the portal and add it to the repository.
    """
    with cd(env.path):
        print(env.local)
        sudo('python manage.py dumpdata --indent 4 static > %(local)s/fixtures/static.json' % env)
        sudo('python manage.py dumpdata --indent 4 treemenus > %(local)s/fixtures/treemenus.json' % env)
        sudo('python manage.py dumpdata --indent 4 blog > %(local)s/fixtures/blog.json' % env)
        sudo('python manage.py dumpdata --indent 4 index > %(local)s/fixtures/index.json' % env)
        sudo('python manage.py dumpdata --indent 4 services > %(local)s/fixtures/services.json' % env)
        # TODO: handle this properly
        #with settings(warn_only=True):
        #    result = sudo('hg commit -u %(user)s -m "[fabfile] Committed latest content to repo."' % env)
        #    if (result.failed and result.return_code == 1):
        #        print(yellow("Nothing changed - leaving as is"))
        #    else:
        #        result = sudo('hg push https://%(user)s:%(password)s@%(repo)s/%(project)' % env)
        #        if (result.failed):
        #            print(red("Could not push the latest commit - please check."))


def user_exists():
    """
        Check if the user exists.
    """
    print('echo "SELECT 1 FROM pg_roles WHERE rolname=\'%(dbuser)s\';" | psql postgres -tA' % env)
    output = run('echo "SELECT 1 FROM pg_roles WHERE rolname=\'%(dbuser)s\';" | psql postgres -tA' % env)
    print("output: " + output)
    if (output == "1"):
        print(green("Good.  User '%(dbuser)s' exists." % env))
        return True
    else:
        return False


def create_user():
    """
        Creates a user.
    """
    if not user_exists():
        print(green("Creating user '%(dbuser)s'." % env))
        output = run('echo "CREATE ROLE %(dbuser)s WITH LOGIN PASSWORD \'%(dbpassword)s\';" | psql postgres -tA' % env)
        if (output == "CREATE DATABASE" or output == "CREATE ROLE"):
            print(green("Created user successfully."))
        else:
            print(red("Could not create user."))
            abort("User creation error.")


def database_exists():
    """
        Check if the database exists.
    """
    output = run('echo "SELECT 1 from pg_database WHERE datname=\'%(dbname)s\';" | psql postgres -tA' % env)
    if (output == "1"):
        print(green("Good.  Database '%(dbname)s' exists." % env))
        return True
    else:
        return False


def create_database():
    if not database_exists():
        print(green("Creating database '%(dbname)s'..." % env))
        output = run('echo "CREATE DATABASE %(dbname)s OWNER %(dbuser)s;" | psql postgres -tA' % env)
        if (output == "CREATE DATABASE"):
            print(green("Created database successfully."))
        else:
            print(red("Could not create database."))
            abort("Database creation error.")


def drop_database():
    """
        Destroys the user and database for this project.
    """
    with settings(warn_only=True):
        run('dropdb %(dbname)s' % env)
        run('dropuser %(dbuser)s' % env)


@task
def update_deployment_time():
    # get date and time
    from datetime import datetime
    now = datetime.now()
    deployment_time = now.strftime("%d.%m.%Y, %H%Mhrs");
    print(green("Deployment time is " + deployment_time + "."))
    # first get Django access
    from sys import path
    path.append(env.path)
    django.settings_module('elevenbits.settings')
    with cd(env.path):
        # get the version
        from elevenbits.templatetags import revision
        version = revision.get_hg_revision()
        # TODO: get tag
        tag = "n/a"
        # add this development
        from elevenbits.deployment.models import Deployment
        deployment = Deployment(tag=tag, timestamp=now, version=version, deployer='Deployed via Fabric.')
        deployment.save()
        

def populate_database():
    """
        Loads (mostly fixture) data in the database.
    """
    with cd(env.path):
        run('./manage.py syncdb')
        run('./manage.py migrate')
        run('./manage.py loaddata static.json')
        run('./manage.py loaddata treemenus.json')
        run('./manage.py loaddata blog.json')
    # update the deployment time
    with cd(env.path + "/bin"):
        run('fab update_deployment_time')


def restart_database():
    sudo("service postgresql restart")
    

def restart_webserver():
    sudo("service nginx restart")
    sudo("service uwsgi restart")


def update_webserver():
    # remove default first
    with settings(warn_only=True):
        sudo("rm /etc/nginx/sites-enabled/default")
    # update nginx
    sudo("mkdir -p /etc/nginx/sites-available" % env)
    sudo("cp %(path)s/conf/%(host)s.conf /etc/nginx/sites-available" % env)
    sudo("ln -sf %(path)s/conf/%(host)s.conf /etc/nginx/sites-enabled/%(host)s.conf" % env)
    # update uwsgi
    sudo("mkdir -p /etc/uwsgi/apps-available" % env)
    sudo("mkdir -p /etc/uwsgi/apps-enabled" % env)
    sudo("cp %(path)s/conf/django.ini /etc/uwsgi/apps-available" % env)
    sudo("ln -sf %(path)s/conf/django.ini /etc/uwsgi/apps-enabled/django.ini" % env)


def create_uwsgi_upstart():
    # TODO: first check if it already exists
    sudo("cp %(path)s/conf/uwsgi.conf /etc/init" % env)
    sudo("initctl reload uwsgi")
