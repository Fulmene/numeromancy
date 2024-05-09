# syntax=docker/dockerfile:1
FROM tensorflow/tensorflow:2.15.0.post1-gpu

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install scipy==1.12.0

RUN pip install nltk==3.8.1
RUN python -m nltk.downloader -d /usr/local/share/nltk_data stopwords

RUN pip install gensim==4.3.2
RUN pip install networkx==3.3
COPY nbne/ ./nbne/
RUN pip install ./nbne/

RUN pip install keras-self-attention==0.51.0

RUN pip install progressbar2==4.4.2

COPY numeromancy/ ./numeromancy/

CMD ["bash"]
