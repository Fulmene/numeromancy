# syntax=docker/dockerfile:1
FROM tensorflow/tensorflow:2.15.0.post1-gpu as base

ARG USER_ID
ARG GROUP_ID

RUN groupadd -g ${GROUP_ID} user
RUN useradd -g ${GROUP_ID} -u ${USER_ID} -m -s /bin/bash user

WORKDIR /home/user/app

RUN pip install scipy==1.12.0

RUN pip install nltk==3.8.1
RUN python -m nltk.downloader -d /usr/local/share/nltk_data stopwords
RUN python -m nltk.downloader -d /usr/local/share/nltk_data punkt

RUN pip install gensim==4.3.2
RUN pip install networkx==3.3
COPY nbne/ ./nbne/
RUN pip install ./nbne/

RUN pip install keras-self-attention==0.51.0

RUN pip install xgboost==2.0.3

RUN pip install progressbar2==4.4.2

USER user

FROM base as dev

USER root
RUN pip install basedpyright

USER user
COPY pyrightconfig.json ./pyrightconfig.json
