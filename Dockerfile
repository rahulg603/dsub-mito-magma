FROM python:3.7-slim-stretch

COPY run_MAGMA.py /home/
COPY gcp_downloader.py /home/
COPY ukbb-round2-a0a59abaac58.json /home/

RUN mkdir -p /usr/share/man/man1 /home/MAGMA/

RUN apt-get update && apt-get -y install wget curl python3-pip python-pip openjdk-8-jdk
RUN apt-get install -y unzip
RUN wget -P /home/MAGMA/ https://ctg.cncr.nl/software/MAGMA/prog/magma_v1.07b.zip
RUN unzip /home/MAGMA/*.zip -d /home/MAGMA/
RUN pip install google-cloud-storage
RUN pip3 install hail

ENV GOOGLE_APPLICATION_CREDENTIALS /home/ukbb-round2-a0a59abaac58.json
ENV SERVICE_ACCOUNT_JSON_PATH /home/ukbb-round2-a0a59abaac58.json
ENV PATH="${PATH}:/home/"
ENV PYTHONPATH "${PYTHONPATH}:/home/"

# testing
# ENV SUMMARY I9_HYPERTENSION.gwas.imputed_v3.both_sexes.tsv
# ENV N 400000
# ENV FOLD vm1
# COPY script_file.py /home/

CMD ["/bin/bash"]