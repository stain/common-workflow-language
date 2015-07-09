FROM grahamdumpleton/mod-wsgi-docker:python-2.7
MAINTAINER soiland-reyes@cs.manchester.ac.uk

## Let's start with some basic stuff.
RUN apt-get update -qq && apt-get install -qqy \
    graphviz

WORKDIR /app
ADD README.rst setup.py /app/
ADD cwltool /app/cwltool
ADD cwltool/schemas/ /app/cwltool/schemas
RUN ls /app
#RUN python setup.py install
RUN pip install .
RUN mod_wsgi-docker-build

EXPOSE 80
ENTRYPOINT [ "mod_wsgi-docker-start" ]
CMD [ "cwltool/webapi.wsgi" ]
