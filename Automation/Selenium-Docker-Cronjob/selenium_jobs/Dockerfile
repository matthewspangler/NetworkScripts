FROM python:3.8-slim-buster
ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update --fix-missing
RUN apt-get install -y \
        cron \
        systemd \
        wget \
        zip unzip \
        vim \
        gcc \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        musl-dev \
        python3-dev \
        python3-pip \
        curl ca-certificates \
    && update-ca-certificates

#set up the Chrome PPA
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Update the package list and install chrome
RUN apt-get update -y
RUN apt-get install -y google-chrome-stable

# Set up Chromedriver Environment variables
ENV CHROMEDRIVER_VERSION 94.0.4606.61
ENV CHROMEDRIVER_DIR /chromedriver
RUN mkdir $CHROMEDRIVER_DIR

# Download and install Chromedriver
RUN wget -q --continue -P $CHROMEDRIVER_DIR "http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
RUN unzip $CHROMEDRIVER_DIR/chromedriver* -d $CHROMEDRIVER_DIR

# Put Chromedriver into the PATH
ENV PATH $CHROMEDRIVER_DIR/chromedriver:$PATH

COPY ./ /home/selenium_jobs/
WORKDIR /home/selenium_jobs

RUN pip3 install -r ./requirements/base_requirements.txt

RUN chmod 755 ./scripts/entrypoint.sh
RUN chmod 755 ./scripts/run_foreman_job.sh
COPY ./scripts/cron_scheduler /etc/cron.d/cron_scheduler
RUN chmod 755 /etc/cron.d/cron_scheduler
RUN crontab /etc/cron.d/cron_scheduler
RUN service cron start

ENTRYPOINT ["./scripts/entrypoint.sh"]

