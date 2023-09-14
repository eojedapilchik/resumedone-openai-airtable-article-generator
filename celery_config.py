broker_url = 'pyamqp://guest:guest@localhost//'
result_backend = 'rpc://'
accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
timezone = 'UTC'
broker_connection_retry_on_startup = True
broker_connection_max_retries = 10