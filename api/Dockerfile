FROM python:3.11

# Install GCC and other build essentials
#RUN #yum install -y gcc-c++ make
WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN pip install uvicorn

COPY . .

#EXPOSE 80

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5789"]
#CMD ["main.handler"]
