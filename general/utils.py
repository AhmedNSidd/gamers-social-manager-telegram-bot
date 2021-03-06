def create_sql_array(data):
    array = ""
    if not data:
        array = "NULL"
    elif type(data[0]) == str:
        array = "ARRAY['{}'".format(data[0])
        for datum in data[1:]:
            array += ", '{}'".format(datum)
        array += "]"
    else:
        array = "ARRAY[{}".format(data[0])
        for datum in data[1:]:
            array += ", {}".format(datum)
        array += "]"
    return array