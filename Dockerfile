FROM tiangolo/uwsgi-nginx:python3.10


ENV APP_DIR /skip-crud-service


# update and install packages
RUN apt-get update
RUN apt install -y build-essential \
                    git \
                    openssh-client \ 
                    ca-certificates \
                    netcat \
                    iputils-ping


# update to the latest pip
RUN pip3 install --upgrade pip


# Our application code will exist in the /app directory,
# so set the current working directory to that
WORKDIR ${APP_DIR}


ADD app ./app
ADD resources ./resources
ADD requirements ./
ADD run.py ./


RUN  pip3 install -r requirements --no-cache-dir


CMD python run.py