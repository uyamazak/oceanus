
# DEPRECATED

This repoository is deprecated in favor of the
sample [here](https://github.com/GoogleCloudPlatform/python-docs-samples/tree/master/appengine/standard/django).
Please see the [associated tutorial](https://cloud.google.com/python/django/appengine).


# Python Django Skeleton for Google App Engine


A skeleton for building Python applications on Google App Engine with the
[Django Web Framework](https://www.djangoproject.com/) using
[Cloud SQL](https://cloud.google.com/sql/docs/introduction).

See our other [Google Cloud Platform github
repos](https://github.com/GoogleCloudPlatform) for sample applications and
scaffolding for other python frameworks and use cases.

Note that this project no longer uses the the SDK-provided Django 1.5 library but
uses `pip -t` to vendor Django 1.9 into the lib/ folder.

This project is based on the introductory [Django Tutorial](https://docs.djangoproject.com/en/1.8/intro/tutorial01/)
polls applications.

## Project Creation

The basic skeleton of this project was created using the standard Django commands:

  *  Use the standard Django command to start the project
   ```
   django-admin startproject mysite
   ```
  * Edit the DATABASE field in mysite/settings.py to use the CloudSQL instance locally,
    and use the Unix socket to talk to the same CloudSQL instance through a Unix socket
    when deployed
  * Create appengine_config.py to ensure that libraries vendored into lib/ are on Python's
    sys.path when run.
  * Create [app.yaml](https://cloud.google.com/appengine/docs/python/config/appconfig?hl=en)
    and setup a static file handler in the same folder that mysite/settings.py is configured
    to collect static files. All other routes are directed to Django's WSGI handler.

## Enable Cloud SQL

This project assumes you are using [CloudSQL](https://cloud.google.com/sql/docs/introduction)
as your database. CloudSQL is a managed MySQL instance hosted by Google Cloud, although you
could also host a MySQL instance elsewhere and use that. Please see instructions below
for how to enable create a CloudSQL instance.

For better scalability, consider
[Cloud Datastore](https://cloud.google.com/datastore/docs/concepts/overview?hl=en), although
you must use a custom backend such as [Djangae](https://github.com/potatolondon/djangae) for your
models to work with it.

## Run Locally
1. Install the [App Engine Python SDK](https://developers.google.com/appengine/downloads).
See the README file for directions. You'll need python 2.7 and [pip 7.0 or later](http://www.pip-installer.org/en/latest/installing.html) installed too.

1. Clone this repo

   ```
   git clone https://github.com/GoogleCloudPlatform/appengine-django-skeleton.git
   ```
1. Install dependencies. There are two types of dependencies. requirements-local.txt contains libraries that are already
   expressed in app.yaml, like MySQL. Since app.yaml includes them in the runtime, they don't need to be installed to deploy the app, but they do need to be installed locally to run the app locally. You can use `pip install -r requirements-local.txt' to install them on your system or in a virtualenv, but the libraries should not be included in the project directory or
   uploaded to App Engine, where instead the bundled version is used.

   requirements-vendor.txt includes dependencies that should be 'vendored', which means its completely included in the directory at
   time of deployment. This can only be done for pure Python libraries that don't require system libraries. In this case, a recent version of Django is vendored. These vendored libaries can be added
   to the project using the `pip -t` flag, which installs it directly into the folder specified, in this case the `lib` folder. In order to make this project deployable directly after clone, the vendored libraries were already checked into this repo, but new ones can be added and then installed using the `pip -t flag`.
   ```
   # vendor Django directly into the project `lib` folder
   pip install -r requirements-vendor.txt -t lib
   # install globally or within a virtualenv for local testing
   pip install -r requirements-local.txt
   ```

1. Setup your Python path. Since Django is being added to the lib/ directory along with other vendored dependencies,
the lib/ directory must be added to your Python import path in order for the libraries to be imported correctly outside
 of App Engine or dev_appserver, such as when you run the Django management console locally.

One way to accomplish this is to use the PYTHONPATH environment variable,
which might look like this (assuming you are running from the repo's directory):

    export PYTHONPATH=$(pwd)/lib

The `pwd` command fills in your current directory (appengine-django-skeleton), so that adds the absolute path of
the lib directory to the Python import path.

Another approach would be to add it to the import path in `manage.py` like this:

    sys.path.append('lib')


1. Create a new CloudSQL instance.

Please note that only 1st generation CloudSQL instance are currently supported for Google App Engine applications.

* From the Google Cloud Console, go to [Storage > CloudSQL> Create Instance](https://console
 .developers.google.com/project/_/sql/create)

* Under [Access Control > IP Address](https://console.developers.google.com/project/_/sql/instances/polls/access-control/ip),  Request IPv4 Address. This address will be your HOST for remote access to the
      CloudSQL instance in mysite/settings.py, so replace `<your-database-host>` with this address.

* Under [Databases](https://console.developers.google.com/project/_/sql/instances/polls/databases), click New Database and create the name for your database in mysite/settings.py. Replace

      `<your-database-name>` with this value.

At this point, your deployed AppEngine application can access the database, after you replace
`<your-project-id>:<your-cloudsql-instance>` and
`<your-database-name>` in mysite/settings.py. The following instructions are to connect to the same CloudSQL instance
locally. Alternatively, you could install a local MySQL instance and use that in development.

* Under [Access Control > Authorization](https://console.developers.google.com/project/_/sql/instances/polls/access-control/authorization) Under "Allowed Networks", click "Add item", and add Network 0.0.0.0/0. This opens up
          access to your CloudSQL instance from any network. Stricter firewall settings should be considered for production
          applications.

* Under  [Access Control > Authorization](https://console.developers.google.com/project/_/sql/instances/polls/access-control/users), Click
          "Create user account". Create a username and password and edit mysite/settings.py DATABASES
          to reflect this. Replace `<your-database-user>` and `<your-database-password>` with these variables.

Note in myproject/settings.py, the deployed app does not use the IP or user created, but instead talks to the instance through a Unix
socket as root. When testing locally, use the settings created above to access the database.

1. Create and run the Django migrations:

    ```
    python manage.py makemigrations polls
    python manage.py migrate
    ```


1. Run this project locally from the command line:

   ```
   dev_appserver.py app.yaml
   ```

  You can also run the server using Django's server, assuming you install the dependencies:
  ```
  python manage.py runserver
  ```

Visit the application [http://localhost:8080](http://localhost:8080)

See [the development server documentation](https://developers.google.com/appengine/docs/python/tools/devserver)
for options when running dev_appserver.

## Deploy
To deploy the application:

1. Use the [Google Developer's Console](https://console.developer.google.com) to create a
   project, and note the project ID created. The project ID is sometimes the project
   name provided, and sometimes an auto-generated name.
1. Collect the static files into the static/ directory
   ```
   python manage.py collectstatic
   ```
1. Verify that `<your-cloud-project-id>` and `<your-database-name>` have been replaced in mysite/settings.py
   with your Cloud Project ID and your database name respectively.
1. [Deploy the
   application](https://developers.google.com/appengine/docs/python/tools/uploadinganapp) using the [Google Cloud SDK](https://cloud.google.com/sdk/?hl=en).

   ```
   gcloud init # only required once
   gcloud app deploy
   ```

1. Congratulations!  Your application is now live at https://your-app-id.appspot.com

### Installing Libraries
See the [Third party
libraries](https://developers.google.com/appengine/docs/python/tools/libraries27)
page for libraries that are already included in the SDK.  To include SDK
libraries, add them in your app.yaml file. Other than libraries included in
the SDK, only pure python libraries may be added to an App Engine project.

Alternatively, pure Python libraries can be added to requirements.txt, and
installed using `pip -t` into the lib/ folder and accessed directly through
there.

### Feedback
Star this repo if you found it useful. Use the github issue tracker to give
feedback on this repo.

## Contributing changes
See [CONTRIBUTING.md](CONTRIBUTING.md)

## Licensing
See [LICENSE](LICENSE)
