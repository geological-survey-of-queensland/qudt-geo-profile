from os.path import dirname, realpath, join
import requests
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, SKOS

# # get the latest all-units RDF file
THIS_DIR = dirname(realpath(__file__))
QUDT_UNITS_FILE_PATH = join(THIS_DIR, 'resources', 'qudt-units.ttl')
QUDT_QKS_FILE_PATH = join(THIS_DIR, 'resources', 'qudt-quantitykinds.ttl')


def update_qudt_units_file():
    with open(QUDT_UNITS_FILE_PATH, 'w') as f:
        r = requests.get('http://qudt.org/2.1/vocab/unit')
        if r.ok:
            f.write(r.text)
            print('Updated QUDT units file')
        else:
            print('Could not get QUDT units file from http://qudt.org/2.1/vocab/unit')
            print(r.status_code)
            print(r.text)
            exit()


def create_geoprofile_units():
    # load the QUDT all units ontology from the QUDT all units file
    g_all = Graph()
    g_all.parse(QUDT_UNITS_FILE_PATH, format='turtle')
    g_prof = Graph()
    g_prof.bind('dcterms', DCTERMS)
    g_prof.bind('skos', SKOS)
    QUDT = Namespace('http://qudt.org/schema/qudt/')
    g_prof.bind('qudt', QUDT)
    UNIT = Namespace('http://qudt.org/vocab/unit/')
    g_prof.bind('unit', UNIT)

    # get UoMs listed in uom.txt from QUDT all units file and put them in units.ttl
    for uom_curie in open(join(THIS_DIR, 'inputs', 'units.txt')).readlines():
        uom_uri = UNIT + uom_curie.strip().replace('unit:', '')
        for s, p, o in g_all.triples((URIRef(uom_uri), None, None)):
            g_prof.add((s, p, o))

    with open(join(THIS_DIR, 'geoprofile', 'units.ttl'), 'w') as f:
        f.write(g_prof.serialize(format='turtle').decode('utf-8'))

    print('Created geoprofile units')


def update_qudt_quantitykinds_file():
    uri = 'https://raw.githubusercontent.com/qudt/qudt-public-repo/master/vocab/quantitykinds/VOCAB_QUDT-QUANTITY-KINDS-ALL-v2.1.ttl'
    with open(QUDT_QKS_FILE_PATH, 'w') as f:
        r = requests.get(uri)
        if r.ok:
            f.write(r.text)
            print('Updated QUDT quantity kinds file')
        else:
            print('Could not get QUDT quantity kinds file from http://qudt.org/2.1/vocab/unit')
            print(r.status_code)
            print(r.text)
            exit()


def create_geoprofile_quantitykinds():
    # load the QUDT quantity kinds vocab from the QUDT quantity kinds file
    g_all = Graph()
    g_all.parse(QUDT_QKS_FILE_PATH, format='turtle')
    g_prof = Graph()
    g_prof.bind('dcterms', DCTERMS)
    g_prof.bind('skos', SKOS)
    QUDT = Namespace('http://qudt.org/schema/qudt/')
    g_prof.bind('qudt', QUDT)
    QK = Namespace('http://qudt.org/vocab/quantitykind/')
    g_prof.bind('qk', QK)

    # get UoMs listed in uom.txt from QUDT all units file and put them in quantitykinds.ttl
    for qk_curie in open(join(THIS_DIR, 'inputs', 'quantitykinds.txt')).readlines():
        qk_uri = QK + qk_curie.strip().replace('qk:', '')
        for s, p, o in g_all.triples((URIRef(qk_uri), None, None)):
            g_prof.add((s, p, o))

    with open(join(THIS_DIR, 'geoprofile', 'quantitykinds.ttl'), 'w') as f:
        f.write(g_prof.serialize(format='turtle').decode('utf-8'))

    print('Created geoprofile quantitykinds')


if __name__ == '__main__':
    # update_qudt_units_file()
    # update_qudt_quantitykinds_file()

    create_geoprofile_units()
    create_geoprofile_quantitykinds()

    print('All complete')
