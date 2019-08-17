FROM jupyter/scipy-notebook

USER jovyan

WORKDIR /usr/src/decomp

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r ./requirements.txt

COPY . .

RUN pip install --user --no-cache-dir .

WORKDIR /home/jovyan/