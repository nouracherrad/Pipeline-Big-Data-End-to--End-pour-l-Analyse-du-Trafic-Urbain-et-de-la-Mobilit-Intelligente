FROM eclipse-temurin:11-jre

# Installer Python et dépendances
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    wget \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Créer lien symbolique python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Installer Spark
ENV SPARK_VERSION=3.3.0
ENV HADOOP_VERSION=3
RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz && \
    mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark && \
    rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Variables d'environnement
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.5-src.zip
ENV JAVA_HOME=/opt/java/openjdk

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt
COPY . .

CMD ["python", "spark_job.py"]
