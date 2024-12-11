FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY remove_subscribers_requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r remove_subscribers_requirements.txt 

COPY remove_subscribers.py ${LAMBDA_TASK_ROOT}
COPY connect_to_database.py ${LAMBDA_TASK_ROOT}


CMD ["remove_subscribers.lambda_handler"]