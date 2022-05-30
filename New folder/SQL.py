from calendar import c
import csv
import json

from blist import sorteddict
from sqlalchemy import ForeignKey
from sympy import Q, primitive

KEYWORDS = ("SELECT","FROM","WHERE","ORDER","BY","ASC","DSC","INSERT","INTO","VALUES","DELETE")
OPERATORS = ("=","!=","<",">","<=",">=","!<","!>")
DIGITS = ("0","1","2","3","4","5","6","7","8","9")
LOGIC_OPRS = ("AND","OR")
COLUMNS = dict()

first_column_name = ""

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
# select name from students
table_name = "students"
error_flag = False

data = sorteddict() # {"0", sorteddict({"name":"osman","surname":"mutlu",...})}

result = {}


def read_csv(csvFile):
    global data,COLUMNS
     # data's keys is index, value is dict = {"row": value,.....}
    with open(csvFile, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        
        for i,rows in enumerate(csvReader):
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
                COLUMNS = dict(zip(columns_list,type_list))
            values = rows[columns_str].split(";")  
            column_dict = sorteddict(zip(COLUMNS.keys(),values))
            data[i] = column_dict
            

def isValid(query):
    global table_name
    query_valid_list = list()
    query.replace("("," ")
    query.replace(")","")
    arr = query.split()
    for i,item in enumerate(arr):
        if query_valid_list in RULES:
            temp_query_valid_list = list()
            rule_index = "R{}".format(RULES.index(query_valid_list))
            temp_query_valid_list.append(rule_index)
            query_valid_list = temp_query_valid_list
            
        if item.upper() in KEYWORDS:
            query_valid_list.append(KEYWORDS.index(item.upper()))
            if i< len(arr)-1 and item.upper() == "FROM" and arr[i+1].upper() != table_name.upper():
                return False
                
        elif item in OPERATORS:
            next_type = ""
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
            query_valid_list.append("log")
        else:
            query_valid_list.append("#")
    if not query_valid_list in RULES:
        return False
    return True

def where_state(query):
    global result,error_flag
    temp_result = {}
    # We have 2 option
    # column_name opr item
    # column_name opr item logic_opr column_name opr item
    query_list = query.upper().split()
    if "AND" in query_list:
        query = query.split()
        temp_str_1 = query[0] + " " + query[1] + " "+ query[2]
        temp_str_2 = query[4] + " " + query[5] + " "+ query[6]
        temp_result_1 = where_state(temp_str_1)
        temp_result_2 = where_state(temp_str_2)
        for key in temp_result_1:
            if key in temp_result_2.keys():
                temp_result[key] = temp_result_1[key]
    elif "OR" in query_list:
        query = query.split()
        temp_str_1 = query[0] + " " + query[1] + " "+ query[2]
        temp_str_2 = query[4] + " " + query[5] + " "+ query[6]
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
                if "!" in opr:
                    opr = opr.replace("!","")
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
                                '''
                if len(query)>1:
                    # query[1] = "Order By DESC"
                    query = query[1].upper().split(" ",2)
                    temp_result = order_state(query[2])'''
    return temp_result
    
def order_state(query):
    temp_result = {}
    if query == "DSC":
        if COLUMNS[first_column_name] == "int":
            temp_result = dict(sorted(result.items(), key = lambda x : int(x[1][first_column_name]),reverse=True))   
        else:
            temp_result = dict(sorted(result.items(), key = lambda x : x[1][first_column_name],reverse=True))   
    elif query == "ASC":
        if COLUMNS[first_column_name] == "int":
            temp_result = dict(sorted(result.items(), key = lambda x : int(x[1][first_column_name])))
        else:
            temp_result = dict(sorted(result.items(), key = lambda x : x[1][first_column_name]))
    return temp_result
    
    
def select_state(query):
    global result,error_flag,first_column_name
    
    query = query.split(" ",1)
    if query[0] != "*":
        if "," in query[0]:
            columns = query[0].split(",")
            for column in columns:
                if not column in COLUMNS.keys():
                    error_flag = True
                    return False
            first_column_name = columns[0]
        elif query[0] in COLUMNS.keys():
            if not query[0] in COLUMNS.keys():
                error_flag = True
                return False
            first_column_name = query[0]
        else:                
            error_flag = True
            return False
    else:
        first_column_name = list(COLUMNS.keys())[0]
     # ["*","from student where grade > 40"]
    for key in data.keys():
        result[key] = dict(data[key])
    temp_query = query[1].split(" ",2)
    if len(temp_query) > 2:
        temp_query = temp_query[2].split(" ",1)
        if "WHERE" in temp_query[0].upper():
            result = where_state(temp_query[1])
        if "ORDER" in temp_query[0].upper():
            temp_query = temp_query[1].split()
            result = order_state(temp_query[1])
        elif "ORDER" in temp_query[1].upper():
            temp_query = temp_query[1].split()
            result = order_state(temp_query[len(temp_query)-1].upper())   
    temp_result = {}
    print(query[0])
    if "," in query[0]:
        columns = query[0].split(",")
        for key in result.keys():
            temp_dict =  dict()
            for column in columns:
                temp_dict[column] = result[key][column]
            temp_result[key] = temp_dict
    elif query[0] in COLUMNS.keys():
        for key in result.keys():
            temp_dict =  dict()
            temp_dict[query[0]] = result[key][query[0]]
            temp_result[key] = temp_dict
    if query[0] != "*":
        result = temp_result
    return True

def insert_state(query):
    return False


def delete_state(query):
    return False

def exit_state():
    return 0
def process_query(query):
    query = query.split(" ",1)
    if query[0].upper() == "SELECT":
        return select_state(query[1])
    elif query[0].upper() == "INSERT":
        return insert_state(query[1]) #deleted insert into
    elif query[0].upper() == "DELETE":
        return delete_state(query[1]) #deleted insert into
    return False
        
def create_json(jsonFile):
    '''
    tempdata = {}
    for key in data.keys():
        tempdata[key] = dict(data[key])
    
    '''
        
    with open(jsonFile,'w',encoding='utf-8') as jsonf:
       jsonf.write(json.dumps(result, indent=4))

def main():
    global result
    csvFile= r'{}.csv'.format(table_name)
    jsonFile= r'{}.json'.format(table_name)
    try:
        read_csv(csvFile)
    except:
        print("Error: Table is not found !!!")
    query=input("Query: ")
    if isValid(query):
        if process_query(query) and not error_flag:
            create_json(jsonFile)
        else:
            result = {}
            print("Wrong query!!!")
    else:
        result = {}
        print("Wrong query!!!")
    #print(COLUMNS)
    '''
    for key in data.keys():
        result[key] = dict(data[key])
    create_json(jsonFile)'''

if __name__ == '__main__':
    main()