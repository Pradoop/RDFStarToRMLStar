import rdflib
import pandas as pd
from pyoxigraph import *
from rdflib import *
import csv
import os


def askFile():
    dir = input("Enter directory:")
    return dir


def retrieveTripleData(my_directory):
    list_id = 0
    # Setup lists for storing in excel
    subject_list = list()
    predicate_list = list()
    object_list = list()
    my_list = list()

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
        for triple in result:
            parent_id = 0
            list_id += 1
            retrieveValues(triple, subject_list, predicate_list, object_list, my_list, parent_id, list_id)

        my_list = [x for x in my_list if x != []]
        final_list = subject_list + object_list
        return final_list


def retrieveValues(my_triple, my_subject_list, my_predicate_list, my_object_list, my_triple_list, my_parent_id, my_list_id):
    # What to do for subject, subject can be a NamedNode, BlankNode or Triple
    new_list = list()
    my_value_subject = my_triple.subject
    if isinstance(my_value_subject, Triple):
        my_parent_id = my_list_id - 1
        retrieveValues(my_value_subject, my_subject_list, my_predicate_list, my_object_list, my_triple_list, my_parent_id, my_list_id)
    else:
        my_value_subject = my_triple.subject.value
        # check empty
        if not my_subject_list:
            my_subject_list.append(my_value_subject)
            new_list.append(my_value_subject)
        # check duplicates
        elif my_value_subject not in my_subject_list:
            my_subject_list.append(my_value_subject)
            new_list.append(my_value_subject)

    # What to do for predicate, predicate can only be a NamedNode
    my_value_predicate = my_triple.predicate.value
    if not my_predicate_list:
        my_predicate_list.append(my_value_predicate)
    # check duplicates
    elif my_value_predicate not in my_predicate_list:
        my_predicate_list.append(my_value_predicate)

    # What to do for object, object can be a NamedNode,  BlankNode,  Triple or literal
    my_value_object = my_triple.object
    if isinstance(my_value_object, Triple):
        my_parent_id = my_list_id - 1
        retrieveValues(my_value_object, my_subject_list, my_predicate_list, my_object_list, my_triple_list, my_parent_id, my_list_id)
    elif isinstance(my_value_object, Literal):
        if isinstance(my_value_object.datatype, NamedNode):
            my_value_object = my_value_object.value
            # check empty
            if not my_object_list:
                my_object_list.append(my_value_object)
                new_list.append(my_value_object)
            # check duplicates
            elif my_value_object not in my_object_list:
                my_object_list.append(my_value_object)
                new_list.append(my_value_object)
    else:
        my_value_object = my_value_object.value
        # check empty
        if not my_object_list:
            my_object_list.append(my_value_object)
            new_list.append(my_value_object)
        # check duplicates
        elif my_value_object not in my_object_list:
            my_object_list.append(my_value_object)
            new_list.append(my_value_object)

    new_list.append(my_list_id)
    new_list.append(my_parent_id)
    if len(new_list) > 2:
        my_triple_list.append(new_list)


def populateSpreadsheet(my_data):
    output = "reverseEngineering.csv"
    my_header = []

    f = open(os.getcwd() + "\\" + output, 'w', newline='')
    writer = csv.writer(f)

    for elements in my_data:
        element_index = my_data.index(elements) + 1
        my_header.append("c" + str(element_index))

    writer.writerow(my_header)
    writer.writerow(my_data)

    #for sublist in my_data:
    #    sublist_index = my_data.index(sublist) + 1
    #    my_header = []
    #    for element in sublist:
    #        element_index = sublist.index(element) + 1
    #        my_header.append("c" + str(sublist_index) + "-" + str(element_index))
    #    writer.writerow(my_header)
    #    writer.writerow(sublist)

    f.close()
    return output


def createMappings(my_directory, my_output_file):
    g = rdflib.Graph()
    filename, file_extension = os.path.splitext(os.getcwd() + "\\" + my_output_file)

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

    with open(os.getcwd() + "\\" + my_output_file, newline='') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            count += 1
            print(count)
            line_header = row
            line_data = next(reader)
            print(line_header)
            print(line_data)

            # triplesMap
            g.add((URIRef(blank.TriplesMap), RDF.type, rr.TriplesMap))
            # LogicalSource
            g.add((URIRef(blank.TriplesMap), rml.logicalSource, child))  # creates array for logicalSource
            g.add((child, rml.referenceFormulation, Literal(file_extension.upper())))  # creates content of array TODO: find out how to get "ql:file extension" in here
            g.add((child, rml.source, Literal(my_output_file)))  # creates content of array

            # subjectMap
            g.add((URIRef(blank.TriplesMap), rml.subjectMap, child2))  # creates array for logicalSource
            g.add((child2, rml.reference, Literal(line_header[0])))  # creates content of array
            g.add((child2, rml.termType, rr.BlankNode))  # creates content of array

            # predicateObjectMap
            g.add((URIRef(blank.TriplesMap), rr.predicateObjectMap, child3))  # creates array for logicalSource
            g.add((child3, rr.predicate, ex.p))  # creates content of array
            g.add((child3, rml.objectMap, child4))  # creates content of array
            g.add((child4, rr.template, Literal(ex + line_header[0])))  # creates content of array

    g.serialize(os.getcwd() + '\\mycsv2rdf.ttl', format='turtle')


if __name__ == '__main__':
    directory = askFile()
    data = retrieveTripleData(directory)
    output_file = populateSpreadsheet(data)
    #createMappings(directory, output_file)
