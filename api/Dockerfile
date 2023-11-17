FROM public.ecr.aws/lambda/python:3.11

# Install GCC and other build essentials
RUN yum install -y gcc-c++ make
#WORKDIR /app

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

COPY . ${LAMBDA_TASK_ROOT}

#EXPOSE 80

ENV PYTHONUNBUFFERED=1

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
CMD ["main.handler"]