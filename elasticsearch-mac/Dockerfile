# Dockerfile-elastic.yml
FROM arm64v8/openjdk:8-jdk-buster

WORKDIR /usr

# add a non root user
RUN useradd -m elasticuser

# Download extras
RUN apt update
RUN apt install -y curl nano

# Download elasticsearch
RUN curl -L -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.8.23.tar.gz
RUN tar -xvf elasticsearch-6.8.23.tar.gz

# Add config
ADD elasticsearch.yml /usr/elasticsearch-6.8.23/config/elasticsearch.yml

# Add scripts
ADD docker-entrypoint.sh /usr/local/bin

# create an empty directory where docker compose will mount a data volume
RUN mkdir /usr/elasticsearch-6.8.23/data

RUN ln -s /usr/elasticsearch-6.8.23 /usr/elasticsearch
RUN ln -s /usr/elasticsearch-6.8.23 /usr/share/elasticsearch


RUN chown -R elasticuser: .
USER elasticuser

ENV JAVA_HOME=/usr/local/openjdk-18/bin/java
ENV discovery.type=single-node
ENV xpack.security.enabled=false
ENV xpack.ml.enabled=false

RUN cd elasticsearch-6.8.23/bin
RUN chown -R elasticuser: elasticsearch-6.8.23

EXPOSE 9200 9300
#RUN ls -1 /usr/elasticsearch
#RUN ls -1 /usr/elasticsearch/config
#RUN cat /usr/share/elasticsearch/config/elasticsearch.yml

CMD cd /usr/elasticsearch-6.8.23/bin/ && ./elasticsearch

