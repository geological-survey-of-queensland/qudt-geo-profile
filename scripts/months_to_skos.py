import glob
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, OWL, TIME

g = Graph().parse("../resources/time-gregorian.ttl", format="turtle")

for s, o in g.subject_objects(predicate=RDF.type):
    g.remove((s, RDF.type, o))
    g.add((s, RDF.type, SKOS.Concept))

for s, o in g.subject_objects(predicate=RDFS.label):
    g.remove((s, RDFS.label, o))
    g.add((s, SKOS.prefLabel, o))
    g.add((s, SKOS.definition, Literal("", lang="en")))

for s, o in g.subject_objects(predicate=TIME.month):
    g.remove((s, TIME.month, o))
    g.add((s, SKOS.notation, o))

with open("../months.skos.ttl", "w") as f:
    f.write(g.serialize(format="turtle").decode("utf-8"))
