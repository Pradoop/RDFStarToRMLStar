import rdflib
import pandas as pd
from pyoxigraph import *
from rdflib import *
from difflib import SequenceMatcher
import urllib.parse
import csv
import os


def askFile():
    directory = input("Enter directory:")
    #print('Directory is: ' + directory)
    return directory


def retrieveTripleData(my_directory):
    # Setup lists for storing in excel
    subject_list = list()
    predicate_list = list()
    object_list = list()

    for filename in os.listdir(my_directory):
        file = os.path.join(my_directory, filename)
        if os.path.isfile(file) and file.endswith(".ttl"):
            result = list(parse(file, "text/turtle"))
        elif os.path.isfile(file) and file.endswith(".nt"):
            result = list(parse(file, "application/n-triples"))
        else:
            print("Something went wrong, please check the directory and make sure that there are no other files in "
                  "the folder besides .ttl and .nt files")
            return
        #print(result)
        for triple in result:
            #print(triple)
            retrieveValues(triple, subject_list, predicate_list, object_list)

        #print("subject_list")
        #print(subject_list)
        #print("predicate_list")
        #print(predicate_list)
        #print("object_list")
        #print(object_list)

        data = subject_list + object_list
        return data


def retrieveValues(my_value, my_subject_list, my_predicate_list, my_object_list):
    # What to do for subject, subject can be a NamedNode, BlankNode or Triple
    my_value_subject = my_value.subject
    if isinstance(my_value_subject, Triple):
        retrieveValues(my_value_subject, my_subject_list, my_predicate_list, my_object_list)
    else:
        my_value_subject = my_value.subject.value
        # check empty
        if not my_subject_list:
            my_subject_list.append(my_value_subject)
        # check duplicates
        if my_value_subject not in my_subject_list:
            my_subject_list.append(my_value_subject)

    # What to do for predicate, predicate can only be a NamedNode
    my_value_predicate = my_value.predicate.value
    my_predicate_list.append(my_value_predicate)

    # What to do for object, object can be a NamedNode,  BlankNode,  Triple or literal
    my_value_object = my_value.object
    if isinstance(my_value_object, Triple):
        retrieveValues(my_value_object, my_subject_list, my_predicate_list, my_object_list)
    elif isinstance(my_value_object, Literal):
        if isinstance(my_value_object.datatype, NamedNode):
            my_value_object = my_value_object.value
            # check empty
            if not my_object_list:
                my_object_list.append(my_value_object)
            # check duplicates
            if my_value_object not in my_object_list:
                my_object_list.append(my_value_object)
    else:
        my_value_object = my_value_object.value
        # check empty
        if not my_object_list:
            my_object_list.append(my_value_object)
        # check duplicates
        if my_value_object not in my_object_list:
            my_object_list.append(my_value_object)


def populateSpreadsheet(my_data):
    my_header = []
    output_file = "reverseEngineering.csv"

    for i in my_data:
        index = my_data.index(i) + 1
        my_header.append("c" + str(index))

    #print("my_header")
    #print(my_header)

    f = open(os.getcwd() + "\\" + output_file, 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(my_header)
    writer.writerow(my_data)
    f.close()

    return output_file


def createMappings(my_directory, my_output_file):
    g = rdflib.Graph()

    rr = rdflib.Namespace('http://www.w3.org/ns/r2rml#')
    rml = rdflib.Namespace('http://semweb.mmlab.be/ns/rml#')
    ql = rdflib.Namespace('http://semweb.mmlab.be/ns/ql##')
    ex = rdflib.Namespace('http://example/')
    blank = rdflib.Namespace('http://example.org/')
    child = BNode()
    child2 = BNode()
    child3 = BNode()
    child4 = BNode()

    g.namespace_manager.bind('rr', rr)
    g.namespace_manager.bind('rml', rml)
    g.namespace_manager.bind('ql', ql)
    g.namespace_manager.bind('rdf', RDF)
    g.namespace_manager.bind('ex', ex)
    g.namespace_manager.bind('', blank)

    df = pd.read_csv(os.getcwd() + "\\" + my_output_file, sep=",")
    for index, row in df.iterrows():
        print((df.to_string(index=False)))


    # triplesMap
    g.add((URIRef(blank.TriplesMap), RDF.type, rr.TriplesMap))
    # LogicalSource
    g.add((URIRef(blank.TriplesMap), rml.logicalSource, child))  # creates array for logicalSource
    g.add((child, rml.referenceFormulation, ql.CSV))  # creates content of array
    g.add((child, rml.source, Literal(my_output_file)))  # creates content of array

    # subjectMap
    g.add((URIRef(blank.TriplesMap), rml.subjectMap, child2))  # creates array for logicalSource
    g.add((child2, rml.reference, Literal("c1")))  # creates content of array
    g.add((child2, rml.termType, rr.BlankNode))  # creates content of array

    # predicateObjectMap
    g.add((URIRef(blank.TriplesMap), rr.predicateObjectMap, child3))  # creates array for logicalSource
    g.add((child3, rr.predicate, ex.p))  # creates content of array
    g.add((child3, rml.objectMap, child4))  # creates content of array
    g.add((child4, rr.template, Literal("http:example/{c2}")))  # creates content of array

    # for filename in os.listdir(my_directory):
    #    file = os.path.join(my_directory, filename)
    #    if os.path.isfile(file) and file.endswith(".ttl"):
    #        result = list(parse(file, "text/turtle"))
    #    elif os.path.isfile(file) and file.endswith(".nt"):
    #        result = list(parse(file, "application/n-triples"))
    #    else:
    #        print("Something went wrong, please check the directory and make sure that there are no other files in "
    #              "the folder besides .ttl and .nt files")
    #        return
    #    print(result)

    # for index, row in df.iterrows():
    #    g.add((URIRef(ex + row['c1']), RDF.type, Literal(row['c1'], datatype=XSD.string)))
    #    g.add((URIRef(ex + row['c2']), RDF.type, Literal(row['c2'], datatype=XSD.string)))
    #    g.add((URIRef(ex + row['c3']), RDF.type, Literal(row['c3'], datatype=XSD.string)))

    g.serialize(os.getcwd() + '\\mycsv2rdf.ttl', format='turtle')


if __name__ == '__main__':
    dir = askFile()
    data = retrieveTripleData(dir)
    output_file = populateSpreadsheet(data)
    createMappings(dir, output_file)
