from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import DC, DCTERMS, RDF, RDFS, SDO, SKOS, OWL, TIME
from itertools import chain


def pylode_expand_graph(g):
    # name
    for s, o in chain(
            g.subject_objects(DC.title),
            g.subject_objects(RDFS.label),
            g.subject_objects(DCTERMS.title)
    ):
        g.add((s, SKOS.prefLabel, o))

    # description
    for s, o in chain(
            g.subject_objects(DC.description),
            g.subject_objects(DCTERMS.description),
            g.subject_objects(RDFS.comment),
            g.subject_objects(SDO.description)
    ):
        g.add((s, SKOS.definition, o))

    # OWL -> SKOS
    # classes as Concepts types
    for s in chain(
            g.subjects(RDF.type, RDFS.Class),
            g.subjects(RDF.type, OWL.Class)
    ):
        g.add((s, RDF.type, SKOS.Concept))

    # SKOS Concept Hierarchy from Class subsumption
    for s, o in g.subject_objects(RDFS.subClassOf):
        if type(o) != BNode:  # stops restrictions being seen as broader/narrower
            g.add((s, SKOS.broader, o))
            g.add((o, SKOS.narrower, s))

    for s, o in g.subject_objects(OWL.equivalentClass):
        g.add((s, SKOS.exactMatch, o))
        g.add((o, SKOS.exactMatch, s))

    # the ontology is now a ConceptScheme
    for s in g.subjects(RDF.type, OWL.Ontology):
        g.add((s, RDF.type, SKOS.ConceptScheme))

        # top concepts
        # if the class is declared here and has no subClassOf
        for s2 in g.subjects(RDF.type, RDFS.Class):
            if (s2, RDFS.subClassOf, None) not in g:
                g.add((s2, SKOS.topConceptOf, s))

        for s2 in g.subjects(RDF.type, OWL.Class):
            if (s2, RDFS.subClassOf, None) not in g:
                g.add((s2, SKOS.topConceptOf, s))

    # SKOS -> SKOS
    # broader / narrower buildout
    for s, o in g.subject_objects(SKOS.broader):
        g.add((o, SKOS.narrower, s))

    for s, o in g.subject_objects(SKOS.narrower):
        g.add((o, SKOS.broader, s))

    for s, o in g.subject_objects(SKOS.topConceptOf):
        g.add((o, SKOS.hasTopConcept, s))

    for s, o in g.subject_objects(SKOS.hasTopConcept):
        g.add((o, SKOS.topConceptOf, s))

    # Agents
    # creator
    for s, o in chain(
            g.subject_objects(DC.creator),
            g.subject_objects(SDO.creator),
            g.subject_objects(SDO.author)  # conflate SDO.author with DCTERMS.creator
    ):
        g.remove((s, DC.creator, o))
        g.remove((s, SDO.creator, o))
        g.remove((s, SDO.author, o))
        g.add((s, DCTERMS.creator, o))

    # contributor
    for s, o in chain(
            g.subject_objects(DC.contributor),
            g.subject_objects(SDO.contributor)
    ):
        g.remove((s, DC.contributor, o))
        g.remove((s, SDO.contributor, o))
        g.add((s, DCTERMS.contributor, o))

    # publisher
    for s, o in chain(
            g.subject_objects(DC.publisher),
            g.subject_objects(SDO.publisher)
    ):
        g.remove((s, DC.publisher, o))
        g.remove((s, SDO.publisher, o))
        g.add((s, DCTERMS.publisher, o))


def qudt_expand_graph(g):
    for s, o in g.subject_objects(predicate=URIRef(QUDT.plainTextDescription)):
        g.add((s, SKOS.definition, Literal(str(o), lang="en")))

    for s in g.subjects(RDF.type, QUDT.QuantityKind):
        g.add((s, RDF.type, SKOS.Concept))
        # g.add((s, RDFS.isDefinedBy, URIRef("http://linked.data.gov.au/def/geoqk")))

    # for s, p, o in g:
    #     if p in [QUDT.symbol, QUDT.ucumCaseInsensitiveCode, QUDT.ucumCode, QUDT.uneceCommonCode]:
    #         g.add((s, SKOS.notation, o))

    for s, p, o in g:
        if type(o) == Literal:
            if o.datatype == QUDT.LatexString or o.datatype == RDF.HTML:
                g.remove((s, p, o))
                g.add((s, p, Literal(str(o), lang="en")))

    for s, p, o in g:
        if p == SKOS.prefLabel:
            g.remove((s, p, o))
            g.add((s, p, Literal(str(o), lang="en")))

    cs = URIRef("http://linked.data.gov.au/def/geoqk")
    g.remove((cs, RDF.type, URIRef("http://www.w3.org/ns/dx/prof/Profile")))
    g.add((cs, RDF.type, SKOS.ConceptScheme))

    g.add((
        cs,
        DCTERMS.source,
        Literal("Derived from the geo-profile of QUDT (http://linked.data.gov.au/def/geou)", lang="en")
    ))

    for s in g.subjects(predicate=RDF.type, object=SKOS.Concept):
        g.add((cs, SKOS.hasTopConcept, s))
        g.add((s, SKOS.topConceptOf, cs))

        if (s, SKOS.definition, None) not in g:
            g.add((s, SKOS.definition, Literal("", lang="en")))

    for s, p, o in g.triples((None, DCTERMS.conformsTo, None)):
        g.remove((s, None, None))  # BNs

    for s, p, o in g:
        if (s, SKOS.broader, o) in g:
            g.remove((s, SKOS.topConceptOf, None))
            g.remove((None, SKOS.hasTopConcept, s))

            g.add((s, SKOS.inScheme, cs))


def slim_down_graph(g, g_out):
    for s, p, o in g:
        if str(p).startswith(str(DCTERMS)) \
                or str(p).startswith(str(SDO)) \
                or str(p).startswith(str(SKOS)) \
                or str(p).startswith(str(OWL)) \
                or str(p).startswith(str(RDF)) \
                or str(p).startswith(str(RDFS)):
            g_out.add((s, p, o))
        if str(o).startswith(str(QUDT)):
            g_out.remove((s, p, o))
    g_out.remove((None, RDFS.label, None))
    g_out.remove((None, RDFS.comment, None))
    g_out.remove((None, DCTERMS.description, None))


g = Graph().parse("../geoqks.ttl", format="turtle")
g_skos = Graph()

g_skos.bind('skos', SKOS)
g_skos.bind('dcterms', DCTERMS)
g_skos.bind('owl', OWL)
g_skos.bind('sdo', SDO)
GEOU = Namespace("http://linked.data.gov.au/def/geou/")
g_skos.bind('geou', GEOU)
QUDT = Namespace("http://qudt.org/schema/qudt/")
g_skos.bind('qudt', QUDT)

pylode_expand_graph(g)
qudt_expand_graph(g)
slim_down_graph(g, g_skos)

with open("../geoqks.skos.ttl", "w") as f:
    f.write(g_skos.serialize(format="turtle").decode("utf-8"))
