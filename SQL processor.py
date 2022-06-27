import csv
import json

from blist import sorteddict


KEYWORDS = ("SELECT","FROM","WHERE","ORDER","BY","ASC","DSC","INSERT","INTO","VALUES","DELETE")
OPERATORS = ("<=",">=","!<","!>","!=","=","<",">")
DIGITS = ("0","1","2","3","4","5","6","7","8","9")
LOGIC_OPRS = ("AND","OR")

# It contains columns names and their types.
COLUMNS = dict()

# Primary keys in table
ID_LIST = list()

first_selected_column_name = ""

# Rule sets for validation.
RULES = (
   [0,"#",1,"#"],
   ["R0",2,"#","opr","#"],
   ["R1",3,4,5],
   ["R1",3,4,6],
   ["R1","log","#","opr","#"],
   ["R4",3,4,5],
   ["R4",3,4,6],
   ["R0",3,4,5],
   ["R0",3,4,6],
   [7,8,"#",9,"#"],
   [10,1,"#",2,"#","opr","#"],
   ["R10","log","#","opr","#"]
)

table_name = "students"
# For wrong transections.
error_flag = False

data = sorteddict() # {"0", sorteddict({"name":"osman","surname":"mutlu",...})}

result = sorteddict()

# Reads the csv and saves data into data dict.
def read_csv(csvFile):
    global data,COLUMNS,ID_LIST
    with open(csvFile, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for i,rows in enumerate(csvReader):
            # rows -> {"id;nam;,surname;......":"108;ahmet;mutlu;...."}
            # column_str -> "id;name;surname;......"
            # column_list -> ["id","name"......]
            # values -> ["108","ahmet","mutlu"]
            if i == 0:
                columns_str = list(rows.keys())[0]
                columns_list = columns_str.split(";")
                values = rows[columns_str].split(";")
                type_list = list()
                for value in values:
                    flag = True
                    for char in value:
                        if not char in DIGITS:
                            flag = False
                    if flag:
                        type_list.append("int")
                    else:
                        type_list.append("string")
                # columns_list -> {"id","name","lastname",....}
                # typel_list -> {"int","string","string",.....}
                COLUMNS = dict(zip(columns_list,type_list))
            
            values = rows[columns_str].split(";")  
            ID_LIST.append(values[0])
            column_dict = sorteddict(zip(COLUMNS.keys(),values))
            # columdict -> {"id:108","name:ahmet",.....}
            data[i] = column_dict
            

def isValid(query): # select * from students ....
    global table_name
    query_valid_list = list() # For compare with rules.
    query = query.replace("("," ") # If query has values(....)
    query = query.replace(")","")
    arr = query.split() # ["select","*","from",.....]
    for i,item in enumerate(arr):
        if query_valid_list in RULES: 
            temp_query_valid_list = list()
            rule_index = "R{}".format(RULES.index(query_valid_list))# If rules matched replace with their index like [R0].
            temp_query_valid_list.append(rule_index)
            query_valid_list = temp_query_valid_list
            
        if item.upper() in KEYWORDS: #If keyword matched, appends the index of keyword.
            query_valid_list.append(KEYWORDS.index(item.upper())) 
            # You must enter the anything else after "FROM". 
            if i< len(arr)-1 and item.upper() == "FROM" and arr[i+1].upper() != table_name.upper():
                return False
        elif item in OPERATORS:
            next_type = ""
            # Checks the types of values right and left side of operators.
            if i<len(arr):
                flag = True
                for char in arr[i+1]: 
                    if not char in DIGITS:
                        flag = False
                if flag:
                    next_type = "int"
                else:
                    next_type = "string"
            if i<=0 and i>=len(arr):
                return False
            elif arr[i-1] not in COLUMNS.keys():
                return False
            elif COLUMNS[arr[i-1]] == "string" and not (item == "!=" or item == "="):
                return False
            elif COLUMNS[arr[i-1]] == "int" and next_type == "string":
                return False
            elif COLUMNS[arr[i-1]] == "string" and next_type == "int":
                return False
            query_valid_list.append("opr")
        elif item.upper() in LOGIC_OPRS:
            # If is the logic operation, appends "logic".
            query_valid_list.append("log")
        else:
            # If item is normal string, appends "#".
            query_valid_list.append("#")
    # Checks the rule set. If dont match with any rule, the query is wrong!
    if not query_valid_list in RULES:
        return False
    return True

def where_state(query):
    global result,error_flag
    temp_result = sorteddict()
    # We have 2 option
    # column_name opr item
    # column_name opr item logic_opr column_name opr item
    query_list = query.upper().split()
    if "AND" in query_list:
        query = query.split()
        temp_str_1 = query[0] + " " + query[1] + " "+ query[2]
        temp_str_2 = query[4] + " " + query[5] + " "+ query[6]
        #query[3] = "AND"
        temp_result_1 = where_state(temp_str_1)
        temp_result_2 = where_state(temp_str_2)
        for key in temp_result_1:
            if key in temp_result_2.keys():
                temp_result[key] = temp_result_1[key]
    elif "OR" in query_list:
        query = query.split()
        temp_str_1 = query[0] + " " + query[1] + " "+ query[2]
        temp_str_2 = query[4] + " " + query[5] + " "+ query[6]
        #query[3] = "OR"
        temp_result_1 = where_state(temp_str_1)
        temp_result_2 = where_state(temp_str_2)
        temp_result = temp_result_1
        for key in temp_result_2:
            if key not in temp_result.keys():
                temp_result[key] = temp_result_2[key]
                
    else:
        for opr in OPERATORS:
            if opr in query:
                not_flag = False
                if "!" in query:
                    query = query.replace("!","")
                    not_flag = True
                query = query.split(opr)
                query[0] = query[0].strip()
                query[1] = query[1].strip()
                column_name = query[0]
                query = query[1].split(" ",1)
                for key in result.keys():
                    if opr == "=":
                        if not_flag == False:
                            if result[key][column_name] == query[0]:
                                temp_result[key] = result[key]
                        elif not_flag == True:
                            if result[key][column_name] != query[0]:
                                temp_result[key] = result[key]
                    elif opr == ">":
                        if not_flag == False:
                            if int(result[key][column_name]) > int(query[0]):
                                temp_result[key] = result[key]
                        elif not_flag == True:
                            if int(result[key][column_name]) <= int(query[0]):
                                temp_result[key] = result[key]
                    elif opr == "<":
                        if not_flag == False:
                            if int(result[key][column_name]) < int(query[0]):
                                temp_result[key] = result[key]
                        elif not_flag == True:
                            if int(result[key][column_name]) >= int(query[0]):
                                temp_result[key] = result[key]
                    elif opr == ">=":
                        if int(result[key][column_name]) >= int(query[0]):
                                temp_result[key] = result[key]
                    elif opr == "<=":
                        if int(result[key][column_name]) <= int(query[0]):
                                temp_result[key] = result[key]
    return temp_result
def order_state(query):
    # https://www.geeksforgeeks.org/python-sort-nested-dictionary-by-key/
    temp_result = dict()
    if query == "DSC":
        if COLUMNS[first_selected_column_name] == "int":
            temp_result = dict(sorted(result.items(), key = lambda x : int(x[1][first_selected_column_name]),reverse=True))   
        else:
            temp_result = dict(sorted(result.items(), key = lambda x : x[1][first_selected_column_name],reverse=True))   
    elif query == "ASC":
        if COLUMNS[first_selected_column_name] == "int":
            temp_result = dict(sorted(result.items(), key = lambda x : int(x[1][first_selected_column_name])))
        else:
            temp_result = dict(sorted(result.items(), key = lambda x : x[1][first_selected_column_name]))
    return temp_result
    
    
def select_state(query):
    # * from ......
    global result,error_flag,first_selected_column_name
    query = query.split(" ",1)
    if query[0] != "*":
        if "," in query[0]:
            columns = query[0].split(",")
            for column in columns:
                if not column in COLUMNS.keys():
                    error_flag = True
                    return False
            first_selected_column_name = columns[0]
        elif query[0] in COLUMNS.keys():
            if not query[0] in COLUMNS.keys():
                error_flag = True
                return False
            first_selected_column_name = query[0]
        else:                
            error_flag = True
            return False
    else:
        first_selected_column_name = list(COLUMNS.keys())[0]
    # query =  ["*","from student where grade > 40"]
    for key in data.keys():
        result[key] = sorteddict(data[key])
    temp_query = query[1].split(" ",2)
    if len(temp_query) > 2:
        temp_query = temp_query[2].split(" ",1)
        # select * from table_name where ........
        if "WHERE" in temp_query[0].upper():
            result = where_state(temp_query[1])
        # select * from table_name order ........
        if "ORDER" in temp_query[0].upper():
            temp_query = temp_query[1].split()
            result = order_state(temp_query[1])
        # select * from table_name where ........ order by
        elif "ORDER" in temp_query[1].upper():
            temp_query = temp_query[1].split()
            result = order_state(temp_query[len(temp_query)-1].upper())   
    temp_result = dict()
    # query = ["*","from student where grade > 40"]
    if "," in query[0]:
        columns = query[0].split(",")
        for key in result.keys():
            temp_dict =  sorteddict()
            for column in columns:
                temp_dict[column] = result[key][column]
            temp_result[key] = temp_dict
    elif query[0] in COLUMNS.keys():
        for key in result.keys():
            temp_dict =  sorteddict()
            temp_dict[query[0]] = result[key][query[0]]
            temp_result[key] = temp_dict
    if query[0] != "*":
        result = temp_result
    return True

def insert_state(query):
    global result,ID_LIST
    # values(val1,val2,....)
    query = query.replace("("," ")
    query = query.replace(")","")
    # val1,val2,....
    query = query.split()
    query = query[1]
    values = query.split(",")
    new_value = sorteddict()
    if len(values) == len(COLUMNS.keys()):
        #{"0",{"id":15,""}}
        flag = False
        for id in ID_LIST:
            if id == values[0]:
                flag = True
                break
        if flag == False:
            ID_LIST.append(values[0])
            for i,column in enumerate(COLUMNS.keys()):
                new_value[column] = values[i]
            data[len(data)] = new_value
            for key in data.keys():
                result[key] = data[key]
            return True
        else:
            return False
    else:
        return False


def delete_state(query): 
    global result
    for key in data.keys():
        result[key] = data[key]
    query = query.split(" ",1)
    if "WHERE" in query[0].upper():
        print(query[1])
        result = where_state(query[1])
    for key in result.keys():
        del data[key]
    result = sorteddict()
    for key in data.keys():
        result[key] = data[key]
    return True

def process_query(query):
    # Process query is must be valid.
    # Select * from name ....
    query = query.split(" ",1)
    if query[0].upper() == "SELECT": # ["select", "* from ......"]
        return select_state(query[1])# * from ......
    elif query[0].upper() == "INSERT":# ["insert","into table_name value(val1,val2,.....)"]
        query = query[1].split(" ",2)
        return insert_state(query[2]) # values(val1,val2,....)
    elif query[0].upper() == "DELETE": # ["delete","from table_name ....."]
        query = query[1].split(" ",2)
        return delete_state(query[2]) # Where cond.....
    return False
        
def create_json(jsonFile):
    # Sort columns.
    tempdata = {}
    for key in result.keys():
        temp_dict = {}
        for column in COLUMNS.keys():
            if column in result[key].keys():
                temp_dict[column] = result[key][column]
        tempdata[key] = temp_dict
   
    with open(jsonFile,'w',encoding='utf-8') as jsonf:
       jsonf.write(json.dumps(tempdata, indent=4))

def main():
    global result
    csvFile= r'{}.csv'.format(table_name)
    jsonFile= r'{}.json'.format(table_name)
    try:
        read_csv(csvFile)
    except:
        print("Error: Table is not found !!!")
    while 1:
        query=input("Query: ")
        if query.upper() == "EXIT":
            break
        if isValid(query):
            if process_query(query) and not error_flag:
                create_json(jsonFile)
                print("Query successfully :)")
                result = sorteddict()
            else:
                result = sorteddict()
                print("Wrong query!!!")
        else:
            result = sorteddict()
            print("Wrong query!!!")

if __name__ == '__main__':
    main()