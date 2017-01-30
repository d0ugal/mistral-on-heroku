import ConfigParser
import os
import traceback
from urlparse import urlparse

from mistral import config
from mistral.api import app


def create_config_file():
    conf = ConfigParser.RawConfigParser()
    conf.set('DEFAULT', 'rpc_backend', 'rabbit')
    conf.set('DEFAULT', 'auth_type', "")

    conf.add_section('pecan')
    conf.set('pecan', 'auth_enable', False)

    conf.add_section('database')
    conf.set('database', 'connection', os.environ['DATABASE_URL'])

    conf.add_section('oslo_messaging_rabbit')
    rbt = urlparse(os.environ['RABBITMQ_BIGWIG_URL'])
    conf.set('oslo_messaging_rabbit', 'rabbit_userid', rbt.username)
    conf.set('oslo_messaging_rabbit', 'rabbit_password', rbt.password)
    conf.set('oslo_messaging_rabbit', 'rabbit_host', rbt.hostname)
    conf.set('oslo_messaging_rabbit', 'rabbit_port', rbt.port)
    conf.set('oslo_messaging_rabbit', 'rabbit_virtual_host',
             rbt.path.lstrip('')[1:])

    with open('mistral.conf', 'wb') as configfile:
        conf.write(configfile)

    with open('mistral.conf') as configfile:
        print(configfile.read())


print("*" * 50)
print(os.environ['RABBITMQ_BIGWIG_URL'])
print(os.environ['DATABASE_URL'])
print("*" * 50)
print("Creating config...")
print("*" * 50)
create_config_file()
config.parse_args(args=[
    '--server', 'api',
    '--config-file', 'mistral.conf'
])

try:
    print("*" * 50)
    print("Starting migration...")
    print("*" * 50)
    print(os.system("mistral-db-manage --config-file mistral.conf upgrade head"))
    print("*" * 50)
    print("Starting populate...")
    print("*" * 50)
    print(os.system("mistral-db-manage --config-file mistral.conf populate"))
    print("*" * 50)
    print("Done.")
    print("*" * 50)
except:
    traceback.print_exc()

application = app.setup_app()
