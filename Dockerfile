FROM python:3.6

WORKDIR /usr/src/decomp

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD python ./setup.py install
CMD python -c "from decomp import uds"