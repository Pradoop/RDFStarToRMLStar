from pyoxigraph import *
import xlsxwriter
import os


def parseFile():
    directory = input("Enter directory:")
    print('Directory is: ' + directory)

    # Setup lists for storing in excel
    subject_list = list()
    predicate_list = list()
    object_list = list()

    for filename in os.listdir(directory):

        file = os.path.join(directory, filename)
        if os.path.isfile(file) and file.endswith("nt"):
            result = list(parse(file, "application/n-triples", base_iri="http://example/p"))
            print(result)
            for triple in result:
                print(triple)
                retrieveValues(triple, subject_list, predicate_list, object_list)

            print("subject_list")
            print(subject_list)
            print("predicate_list")
            print(predicate_list)
            print("object_list")
            print(object_list)

            data = (subject_list, object_list)
            populateSpreadsheet(data)


def retrieveValues(my_value, my_subject_list, my_predicate_list, my_object_list):
    # What to do for subject, subject can be a NamedNode, BlankNode or Triple
    my_value_subject = my_value.subject
    if isinstance(my_value_subject, Triple):
        retrieveValues(my_value_subject, my_subject_list, my_predicate_list, my_object_list)
    else:
        my_value_subject = my_value.subject.value
        my_subject_list.append(my_value_subject)

    # What to do for predicate, predicate can only be a NamedNode
    my_value_predicate = my_value.predicate.value
    my_predicate_list.append(my_value_predicate)

    # What to do for object, object can be a NamedNode,  BlankNode,  Triple or literal
    my_value_object = my_value.object
    if isinstance(my_value_object, Triple):
        retrieveValues(my_value_object, my_subject_list, my_predicate_list, my_object_list)
    elif isinstance(my_value_object, Literal):
        my_value_object = my_value_object.value
        my_object_list.append(my_value_object)
    else:
        my_value_object = my_value_object.value
        my_object_list.append(my_value_object)



def populateSpreadsheet(my_data):
    workbook = xlsxwriter.Workbook('reverseEngineering.xlsx')
    worksheet = workbook.add_worksheet()

    row = 0
    column = 0

    print(my_data)
    for subj in my_data:
        for value in subj:
            worksheet.write(row, column, value)
            column += 1
        column = 0
        row += 1

    workbook.close()


if __name__ == '__main__':
    parseFile()
