FROM python:2.7

RUN mkdir /oceanus/
COPY django /oceanus/django
WORKDIR /oceanus/django

RUN pip install --upgrade -q \
pip \
requests \
django-debug-toolbar \
django==1.9

RUN pip install --upgrade -r requirements-vendor.txt -t lib/
RUN pip install --upgrade -r requirements-local.txt


EXPOSE 8000

CMD ["bash"]
