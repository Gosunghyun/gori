FROM        gsh2448/gori-front
MAINTAINER  gsh2448.com


WORKDIR     /srv/app/django_app

EXPOSE      80
CMD ["supervisord", "-n"]