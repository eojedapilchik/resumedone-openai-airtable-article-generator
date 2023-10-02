# resumedone-openai-airtable-article-generator
v 1.1

## Configuration
1. Create the LemList webhooks to point to the FastAPI server, endpoint: `/webhook/email_replied/`
2. Add email tags to the email account to be used: "Campaign", "First Reply", "Second Reply", "Third Reply"
3. Add the email account to the environment variables: `GMAIL_SENDER_{ACCOUNT}=account@email.com`, i.e. `GMAIL_SENDER_INFO=info@resumedone.io`
4. Add the credentials file to the root directory of the project: `credentials_{account}.json`, i.e. `credentials_info.json` 

## Commands

1. Starting the Worker:
```bash
celery -A your_module_containing_celery_app worker --loglevel=info
celery -A tasks worker --loglevel=INFO
```
2. Starting the Beat:
```bash
celery -A your_module_containing_celery_app beat
```

3. Checking Worker Status with celery status:
```bash
celery -A your_module_containing_celery_app status
```

4. Starting the Flower:
```bash
celery -A your_module_containing_celery_app flower
```

5. Inspecting Active Tasks with celery inspect scheduled:
```bash
celery -A your_module_containing_celery_app inspect scheduled
```

6. Monitoring with celery events:
```bash
celery -A your_module_containing_celery_app events --mode=top
```

7. Monitoring with celery flower:
```bash
pip install flower
celery -A your_module_containing_celery_app flower
```

8. Upgrade celery config:
```bash
celery upgrade settings celery_config.py
```

### Docker Commands for RabbitMQ:
```bash
docker run -d --hostname my-rabbit --name rabbitmq -p 8080:15672 rabbitmq:3-management
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```

Pull the conainer:
```bash
docker pull rabbitmq:management
```

Access the RabbitMQ Management Console:
```bash
http://localhost:15672/
```

Shutdown and remove the container:
```bash
docker stop rabbitmq
docker rm rabbitmq
```

### FastAPI Commands:
```bash
uvicorn main:app --host 0.0.0.0
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
