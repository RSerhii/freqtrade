FROM python:3.7.5-slim-stretch

RUN apt-get update \
    && apt-get -y install curl build-essential libssl-dev git \
    && apt-get clean \
    && pip install --upgrade pip

# Prepare environment
RUN mkdir /freqtrade
WORKDIR /freqtrade

# Install TA-lib
COPY build_helpers/* /tmp/
RUN cd /tmp && /tmp/install_ta-lib.sh && rm -r /tmp/*ta-lib*

ENV LD_LIBRARY_PATH /usr/local/lib

# Install dependencies
COPY requirements.txt requirements-common.txt requirements-hyperopt.txt /freqtrade/
RUN pip install numpy --no-cache-dir \
  && pip install -r requirements-hyperopt.txt --no-cache-dir

# Install and execute
COPY . /freqtrade/
RUN pip install -e . --no-cache-dir
ENTRYPOINT ["freqtrade"]
# Default to trade mode
CMD [ "trade" ]
