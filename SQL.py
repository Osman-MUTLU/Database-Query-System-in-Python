import csv
import json

from blist import sorteddict

KEYWORDS = ("SELECT","FROM","WHERE","ORDER","BY","ASC","DSC","INSERT","INTO","VALUES","DELETE")
OPERATORS = ("=","!=","<",">","<=",">=","!<","!>")
DIGITS = ("0","1","2","3","4","5","6","7","8","9")
LOGIC_OPRS = ("AND","OR")
COLUMNS = dict()

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


data = sorteddict()
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
                print(values)
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
        print(COLUMNS)
            

def isValid(query):
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
def create_json(jsonFile):
    '''
    tempdata = {}
    for key in data.keys():
        tempdata[key] = dict(data[key])
    
    '''
        
    with open(jsonFile,'w',encoding='utf-8') as jsonf:
       jsonf.write(json.dumps(result, indent=4))

def main():
    csvFile= r'students.csv'
    jsonFile= r'students.json'
    
    #read_csv(csvFile)
    
    query=input("Query: ")
    if isValid(query):
        print(True)
    
    #create_json(jsonFile)

if __name__ == '__main__':
    main()