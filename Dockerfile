# syntax=docker/dockerfile:1
FROM tensorflow/tensorflow:2.19.0-gpu
# FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-devel

ARG USER_ID
ARG GROUP_ID

RUN groupadd -g ${GROUP_ID} user
RUN useradd -g ${GROUP_ID} -u ${USER_ID} -m -s /bin/bash user

WORKDIR /workspace

RUN pip install pandas
RUN pip install scikit-learn
RUN pip install torch torchvision torchaudio

RUN pip install nltk
RUN python -m nltk.downloader -d /usr/share/nltk_data stopwords
RUN python -m nltk.downloader -d /usr/share/nltk_data punkt
RUN python -m nltk.downloader -d /usr/share/nltk_data punkt_tab

RUN pip install gensim
RUN pip install networkx
COPY nbne/ ./nbne/
RUN pip install ./nbne/

RUN pip install transformers
RUN pip install xgboost

RUN pip install progressbar2

RUN pip install basedpyright

USER user
COPY pyrightconfig.json ./pyrightconfig.json
