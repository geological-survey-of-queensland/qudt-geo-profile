import glob
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS, OWL, TIME

# g = Graph().parse("../inputs/result-type.ttl", format="turtle")
# results = []
# for s in g.subjects(predicate=RDF.type, object=SKOS.Concept):
#     results.append(str(s).replace("http://linked.data.gov.au/def/result-type/", "res:"))
#
# with open("../inputs/quantitykinds.txt", "w") as f:
#     f.write("\n".join(sorted(results)))

g = Graph()

# bind prefixes
QUDT = Namespace("http://qudt.org/vocab/unit/")
g.bind("unit", QUDT)
# g.bind("greg", Namespace("http://www.w3.org/ns/time/gregorian/"))
g.bind("geou", Namespace("http://linked.data.gov.au/def/geou/"))

# load target onts
g.parse("../resources/qudt-units.ttl", format="turtle")
# g.parse("../resources/time-gregorian.ttl", format="turtle")

g_out = Graph()
g_out.bind("unit", Namespace("http://qudt.org/vocab/unit/"))
# g_out.bind("greg", Namespace("http://www.w3.org/ns/time/gregorian/"))
g_out.bind("geou", Namespace("http://linked.data.gov.au/def/geou/"))
g_out.bind("qudt", Namespace("http://qudt.org/schema/qudt/"))
g_out.bind("dcterms", Namespace("http://purl.org/dc/terms/"))
g_out.bind("time", TIME)
g_out.bind("qudts", Namespace("http://qudt.org/schema/"))
g_out.bind("owl", OWL)
g_out.bind("", Namespace("http://linked.data.gov.au/def/geou"))
g_out.bind("skos", SKOS)

for f in glob.glob("../inputs/units-*.txt"):
    for l in open(f).readlines():
        # replace prefix with URI
        l2 = l.replace("unit:", "http://qudt.org/vocab/unit/") \
            .replace("geou:", "http://linked.data.gov.au/def/geou/")
            # .replace("greg:", "http://www.w3.org/ns/time/gregorian/")\

        l2 = l2.strip()
        if (URIRef(l2), RDF.type, None) in g:
            for s, p, o in g.triples((URIRef(l2), None, None)):
                g_out.add((s, p, o))
            g_out.add((URIRef(l2), RDF.type, QUDT.Unit))  # just to ensure all Months are also Units
        else:
            g_out.add((URIRef(l2), RDF.type, QUDT.Unit))
            g_out.add((URIRef(l2), RDFS.label, Literal("", lang="en")))
            g_out.add((URIRef(l2), DCTERMS.description, Literal("", lang="en")))
            g_out.add((URIRef(l2), QUDT.conversionOffset, Literal("")))
            g_out.add((URIRef(l2), QUDT.hasQuantityKind, Literal("")))
            g_out.add((URIRef(l2), QUDT.symbol, Literal("")))
            g_out.add((URIRef(l2), RDFS.isDefinedBy, URIRef("http://linked.data.gov.au/def/geou")))

with open("../geoprofile/units.ttl", "w") as f:
    f.write(g_out.serialize(format="turtle").decode("utf-8"))
