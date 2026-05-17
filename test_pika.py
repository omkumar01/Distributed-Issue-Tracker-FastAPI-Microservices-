import pika

def test_url(url):
    try:
        params = pika.URLParameters(url)
        print(f"URL: {url} -> vhost: '{params.virtual_host}'")
    except Exception as e:
        print(f"URL: {url} -> ERROR: {e}")

test_url("amqp://guest:guest@rabbitmq:5672")
test_url("amqp://guest:guest@rabbitmq:5672/")
test_url("amqp://guest:guest@rabbitmq:5672//")
test_url("amqp://guest:guest@rabbitmq:5672/%2F")
