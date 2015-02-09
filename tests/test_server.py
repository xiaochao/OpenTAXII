import pytest
import tempfile

from taxii_server.server import TAXIIServer
from taxii_server.options import ServerConfig

from taxii_server.persistence.sql import SQLDB
from taxii_server.persistence import DataStorage

INBOX = dict(
    id = 'inboxA',
    type = 'inbox',
    description = 'inboxA description',
    destination_collection_required = 'yes',
    address = '/relative/path',
    accept_all_content = 'yes',
    protocol_bindings = ['urn:taxii.mitre.org:protocol:http:1.0', 'urn:taxii.mitre.org:protocol:https:1.0']
)

DISCOVERY_INTERNAL = dict(
    id = 'discoveryA',
    type = 'discovery',
    description = 'discoveryA description',
    address = '/relative/discovery',
    advertised_services = ['inboxA', 'discoveryA'],
    protocol_bindings = ['urn:taxii.mitre.org:protocol:http:1.0']
)

DISCOVERY_EXTERNAL = dict(
    id = 'discoveryB',
    type = 'discovery',
    description = 'discoveryB description',
    address = 'http://example.com/a/b/c',
    protocol_bindings = ['urn:taxii.mitre.org:protocol:http:1.0']
)

INTERNAL_SERVICES = [INBOX, DISCOVERY_INTERNAL]
SERVICES = INTERNAL_SERVICES + [DISCOVERY_EXTERNAL]

DOMAIN = 'example.com'

@pytest.fixture(scope='module')
def server():

    tempdir = tempfile.mkdtemp()
    db_connection = 'sqlite:///%s/server.db' % tempdir
    storage = DataStorage(api=SQLDB(db_connection, create_tables=True))
    
    config = ServerConfig.load(services_properties=SERVICES)
    server = TAXIIServer(DOMAIN, services_properties=config.unpacked_services, storage=storage)

    return server


def test_services_configured(server):
    assert len(server.services) == len(SERVICES)
    assert len(server.path_to_service) == len(INTERNAL_SERVICES)

    assert server.path_to_service[DISCOVERY_INTERNAL['address']].id == 'discoveryA'

    assert all(map(lambda x: x.address.startswith(DOMAIN), server.path_to_service.values()))


