#run this file on the root directory of zinc source, it will output the new cpp files into a new output folder.


import os
import re
from operator import itemgetter, attrgetter
globalSummary = True
cToCppClassObjectList = []
enumeratorNotFoundList = []
methodNotFoundList = []
seeAlsoNotFoundList = []
targe_dir = "libzinc_doxgen_script/auto_comments_output"

def getFilename():
    hFilenames = []
    hppFilenames = []
    typesFilenames = []
    for dirname, dirnames, filenames in os.walk('./core/source/api/zinc'):
        if '.svn' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.svn')
        if 'types' in dirname:
            for filename in  sorted(filenames):
                typesFilenames.append([dirname, filename])
        else:
            for filename in sorted(filenames):
                if '.hpp' in filename:
                    hppFilenames.append([dirname, filename])
                else:
                    hFilenames.append([dirname, filename])
    return hFilenames, hppFilenames, typesFilenames

def summary(hFilenames, hppFilenames, typesFilenames):
    print "C headers: " + str(len(hFilenames)) + " files total"
    for filename in hFilenames:
        print filename;
    print "CPP headers:" + str(len(hppFilenames)) + " files total"
    for filename in hppFilenames:
        print filename;
    print "Type headers:" + str(len(typesFilenames)) + " files total"
    for filename in typesFilenames:
        print filename;
        
def match_pair(hFilenames, hppFilenames, typesFilenames):
    pair_list = []
    for filename in hppFilenames:
       matchNames = [] 
       shortName = filename[1][:-4]
       for hHeaderName in hFilenames:
           if shortName in hHeaderName[1]:
               matchNames.append(hHeaderName)
       for typeHeaderName in typesFilenames:
           if shortName in typeHeaderName[1]:
               matchNames.append(typeHeaderName)
       pair_list.append([filename, matchNames])
    return pair_list

def getCCommentFromPositionBackward(hHeaderContent, position):
    commentsBlock = []
    currentCommentLine = hHeaderContent[position]
    if True == ("*/" in currentCommentLine):
        commentsBlock.append(currentCommentLine)
        currentCommentLinePosition = position-1
        currentCommentLine = hHeaderContent[currentCommentLinePosition]
        commentsBlock.insert(0, currentCommentLine)
        while False == ("/*" in currentCommentLine):
            currentCommentLinePosition = currentCommentLinePosition - 1
            currentCommentLine = hHeaderContent[currentCommentLinePosition]
            commentsBlock.insert(0, currentCommentLine)
    return commentsBlock

# this return a list of tuples containing the functions name and comments block
def createAPIsCommentsTuple(hHeaderContent):
    apiCommentList = []
    length  = len(hHeaderContent)
    current_position = 0
    while current_position < length:
        line = hHeaderContent[current_position]
        short = line[:8]
        name = line[9:]
        #API function found, getting the whole function name 
        if short == 'ZINC_API':
            commentsBlock = getCCommentFromPositionBackward(hHeaderContent, current_position-1)
            current_line = name
            function_with_arguments = name
            while False == (");" in current_line):
                current_position = current_position + 1
                current_line = hHeaderContent[current_position]
                function_with_arguments = function_with_arguments + current_line
            apiCommentList.append([function_with_arguments, commentsBlock])
        current_position = current_position + 1
    return apiCommentList

def getCallerObjectString(api,debug=False):
    objectString = ''
    enum_check = api[:4]
    if ('enum' == enum_check):
        api_copy = api[5:]
    else:
        api_copy = api
    api_copy = api_copy.replace('\n','')
    api_copy = api_copy.replace('\t','')
    if (',' in api):
        objectString = re.findall('\(([^$]*)\,', api_copy)
    else:
        objectString = re.findall('\(([^$]*)\)', api_copy)
    if debug:
        print api_copy
    argument =''
    if len(objectString) > 0:
        temp_argument = objectString[0]
        while temp_argument[0] ==  ' ':
            temp_argument = temp_argument[1:]
        argument = temp_argument
    if debug:
        print '--------------------'
        print argument
  #  argument = argument.replace('\n','')
  #  argument = argument.replace('\t','')
    argumentName = re.findall(' ([^$]*)', argument)
    argumentObjectString = re.findall('([^$]*) ', argument)
    while (' ' in argumentObjectString[0]):
        argumentObjectString = re.findall('([^$]*) ', argumentObjectString[0])
    if debug:
        print argumentName[0]
    while ',' in argumentName[0]:
        if debug:
            print argumentName[0]
        argumentName = re.findall('([^$]*),', argumentName[0])
    if ',' in argumentName[0]:
        argumentName = re.findall(argumentObjectString+' ([^$]*),', argumentName[0])
    returnArgumentName = argumentName[0]
    if '*' in returnArgumentName:
        returnArgumentName = returnArgumentName.replace('*', '')
    return argumentObjectString[0], returnArgumentName

def cToCppName(api):
    reducedName = api.replace('cmzn_','')
    reducedName = reducedName.replace('_id','')
    subStrings = re.split('_', reducedName)
    cppObjectName = ''
    for string in subStrings:
        cppObjectName = cppObjectName + string.title()
    return cppObjectName

class FunctionClassObject:
    def __init__(self, function, className, object):
        self.function = function
        self.className = className
        self.object = object
    def __repr__(self):
        return repr((self.function, self.className, self.object))

def getCppFunctionName(api, argumentObjectString):
    if 'enum_from_string' in api:
        return False
    returnEnumString = api[:5]
    cFunctionName = ''
    cFunctionName =  re.findall(' ([^$]*)\(', api)
    
    if len(cFunctionName) == 0:
        cFunctionName =  re.findall('\n*([^$]*)\(', api)
    cppFunctionName = ''
    if len(cFunctionName) > 0:
        cFunctionName = cFunctionName[0]
    if (' ' in cFunctionName):
        cFunctionName =  re.findall(' ([^$]*)', cFunctionName)
        if len(cFunctionName) > 0:
            cFunctionName = cFunctionName[0]
    if ('\n' in cFunctionName):
        cFunctionName =  re.findall('\n([^$]*)', cFunctionName)
        if len(cFunctionName) > 0:
            cFunctionName = cFunctionName[0]      
    if ('\t' in cFunctionName):
        cFunctionName = cFunctionName.replace('\t','')
    if ('*' in cFunctionName):
        cFunctionName = cFunctionName.replace('*','')
    fullCFunctionName = cFunctionName
    reducedObjectString = argumentObjectString.replace('id','')
    cFunctionName = cFunctionName.replace(reducedObjectString,'')
    subStrings = re.split('_', cFunctionName)
    i = 0;
    for string in subStrings:
        if i == 0:
            cppFunctionName = cppFunctionName + string
            i = 1
        else:
            if string == 'rgb':
                cppFunctionName = cppFunctionName + 'RGB'
            else:
                cppFunctionName = cppFunctionName + string.title()
    cppFunctionName =  cppFunctionName.replace('\n','')
    global cToCppClassObjectList   
    cToCppClassObjectList.append(FunctionClassObject(fullCFunctionName, cToCppName(argumentObjectString), cppFunctionName))
    return cppFunctionName

#convert c comment block to cpp
def cCommentToCpp(commentsBlock, argumentName):
    cppCommentBlock = ''
    paramObjectName = '@param ' + argumentName
    paramObjectName2 = '@param  ' + argumentName
    for commentLine in commentsBlock:
        if False == (paramObjectName in commentLine) and False == (paramObjectName2 in commentLine):
            cppCommentBlock = cppCommentBlock + commentLine
    return cppCommentBlock

class cppComment:
    def __init__(self, className, functionName, comments):
        self.className = className
        self.functionName = functionName
        self.comments = comments
    def __repr__(self):
        return repr((self.className, self.functionName, self.comments))

#This will return a tuple containing caller object name, 
#API++ function name and adjust comment block suitable for API++ 
def processAPIComment(apiComment):
    processAPICommentTuple =[]
    api = apiComment[0]
    commentBlock = apiComment[1]
    argumentObjectString, argumentName = getCallerObjectString(api)
    cppFunctionName = getCppFunctionName(api, argumentObjectString)
    if False != cppFunctionName:
        cppArgumentObjectString = cToCppName(argumentObjectString)
        cppCommentsBlock = cCommentToCpp(apiComment[1], argumentName)
        return cppComment(cppArgumentObjectString, cppFunctionName, cppCommentsBlock)
    else:
        return False

# this function returns a list of tuples containing c++ object name, method
#and c++ comments
def createcppCommentsForFiles(hHeader):
    hHeaderContent = []
    with open(hHeader) as f:
        hHeaderContent = f.readlines()
    apiCommentList = createAPIsCommentsTuple(hHeaderContent)
    processedAPICommentList =[]
    for apiComment in apiCommentList:
        prcossedComment = processAPIComment(apiComment)
        if False != prcossedComment:
            processedAPICommentList.append(prcossedComment)
    return processedAPICommentList
   
def createCFunctionCommentMap(hHeaders):
    cppCommentMap = []
    for item in hHeaders:
        hHeader = os.path.join(item[0], item[1])
        cppCommentMap.extend(createcppCommentsForFiles(hHeader))
    sortedMap = sorted(cppCommentMap, key=attrgetter('className', 'functionName')) 
    return sortedMap

class enumComments:
    def __init__(self, enumeratorName, comments, enumsTuple):
        self.enumeratorName = enumeratorName
        self.comments = comments
        self.enumsTuple = enumsTuple
    def __repr__(self):
        return repr((self.enumeratorName, self.comments, self.enumsTuple))

def createEnumsCommentsListForEnumeration(typesHeaderContent, lineNumber):
    enumsList = []
    currentLineNumber = lineNumber
    currentLine = typesHeaderContent[currentLineNumber]
    while False == ('}' in currentLine):
        minedebug = False
        enum = ''
        comment = ''
        if ('/**<' in currentLine) or ('/*!<' in currentLine):
            mydebug = False
            tempNumber = currentLineNumber
            tempLine = currentLine
            enumFound = False
            continueSearch = False
            if ('*/' in currentLine):
                comment = re.findall('\/\*([^$]*)\*\/', currentLine)[0]
                comment = '/*' + comment + '*/'
            else:
                comment = re.findall('\/\*([^$]*)\n', currentLine)[0]
                comment = '/*' + comment + '\n'
                currentLineNumber = currentLineNumber + 1
                currentLine = typesHeaderContent[currentLineNumber]
                commentToAdd = ''
                while False == ('*/' in currentLine):
                    commentToAdd = re.findall('([^$]*)\n', currentLine)[0]
                    commentToAdd = commentToAdd + '\n'
                    comment = comment + commentToAdd
                    currentLineNumber = currentLineNumber + 1
                    currentLine = typesHeaderContent[currentLineNumber]
                commentToAdd = re.findall('([^$]*)\*\/', currentLine)[0]
                commentToAdd = commentToAdd + '*/'
                comment = comment + commentToAdd
            comment = comment.replace('\t', '')
            if ('convenient value representing' in comment):
                tempNumber = tempNumber - 2
                tempLine = typesHeaderContent[tempNumber]
            while False == enumFound:
                comPos = tempLine.find(',')
                equalPos = tempLine.find('=')
                commentPos = tempLine.find('/*')
                if (comPos == -1 or comPos > commentPos ) and (equalPos == -1 or equalPos > commentPos):
                    if ('/*' in tempLine):
                        enum = re.findall('([^$]*)\/\*', tempLine)[0]
                        enum = enum.replace(' ','')
                        enum = enum.replace('\t','')
                        if (len(enum) > 0):
                            enumFound = True
                    else:
                        enum = tempLine
                        enum = enum.replace(' ','')
                        enum = enum.replace('\t','')
                        if (len(enum) > 0):
                            enumFound = True
                    tempNumber = tempNumber - 1
                    tempLine = typesHeaderContent[tempNumber]
                else:
                    if (equalPos > -1) and (equalPos < commentPos):
                        enum = re.split('=', tempLine)[0]
                        enumFound = True
                    elif (comPos > -1) and (comPos < commentPos):
                        enum = re.split(',', tempLine)[0]
                        enumFound = True
                    enum = enum.replace(' ','')
                    enum = enum.replace('\t','')      
            while ('=' in enum):
                enum = re.findall('([^$]*)=', enum)[0]
            enum = enum.replace(' ','')
            enum = enum.replace('\t','')      
            enum = enum.replace('\n','')
            enum = enum.replace(',','')
            enumsList.append([enum, comment])
        currentLineNumber = currentLineNumber + 1
        currentLine = typesHeaderContent[currentLineNumber]
    
    return enumsList, currentLineNumber

def createEnumerationsCommentsTuple(typesHeaderContent):
    enumCommentList = []
    length  = len(typesHeaderContent)
    current_position = 0
    while current_position < length:
        line = typesHeaderContent[current_position]
        if 'enum' in line:
            current_position = current_position + 1
            currentLine = typesHeaderContent[current_position]
            if '{' in currentLine:
                enumerationString = re.findall('enum ([^$]*)\n', line)
                if len(enumerationString) > 0:
                    enumerationString = enumerationString[0]
                    enumerationCommentLists = getCCommentFromPositionBackward(typesHeaderContent, current_position - 2)
                    enumerationComment = ''
                    if len(enumerationCommentLists) > 0:
                        for enumerationCommentLine in enumerationCommentLists:
                            enumerationComment = enumerationComment + enumerationCommentLine
                        enumerationComment = enumerationComment.replace('\t', '')
                    #print '====================='
                    #print enumerationString
                    enumsTuple, current_position = createEnumsCommentsListForEnumeration(typesHeaderContent, current_position + 1)
                    enumCommentList.append(enumComments(enumerationString, enumerationComment, enumsTuple))
        current_position = current_position + 1
    return enumCommentList

def createEnumCommentsForFiles(typesHeader):
    typesHeaderContent = []
    with open(typesHeader) as f:
        typesHeaderContent = f.readlines()
    enumCommentList = createEnumerationsCommentsTuple(typesHeaderContent)
    return enumCommentList

def createEnumMap(typesHeaders):
    enumMap = []
    for item in typesHeaders:
        if False == ('.hpp' in item[1]):
            typesHeader = os.path.join(item[0], item[1])
        #if pair[1][0][1] == 'sceneviewer.h':
        #    print '=================='
        #    print "sceneviewer.h"
            
            enumMap.extend(createEnumCommentsForFiles(typesHeader))
    sortedMap = sorted(enumMap, key=attrgetter('enumeratorName'))
    #sortedMap = sorted(cppCommentMap, key=attrgetter('className', 'functionName')) 
    return sortedMap

class classComments:
    def __init__(self, className, comments):
        self.className = className
        self.comments = comments
    def __repr__(self):
        return repr((self.className, self.comments))
    
def createClassComments(typesHeaderContent):
    classCommentList = []
    length  = len(typesHeaderContent)
    line_position = 0
    while line_position < length:
        line = typesHeaderContent[line_position]
        short = line[:7]
        if 'struct ' == short:
            className = line[7:]
            className = className.replace('\n', '')
            className = className.replace(';', '')
            className = cToCppName(className)
            current_position = line_position - 1
            currentLine = typesHeaderContent[current_position]
            comment = ''
            if '*/' in currentLine:
                while False == ('/*' in currentLine): 
                    comment = currentLine + comment
                    current_position = current_position - 1
                    currentLine = typesHeaderContent[current_position]
                comment = currentLine + comment
                classCommentList.append(classComments(className, comment))
        line_position = line_position + 1
    return classCommentList    

def createClassCommentsForFiles(typesHeader):
    typesHeaderContent = []
    with open(typesHeader) as f:
        typesHeaderContent = f.readlines()
    classCommentList = createClassComments(typesHeaderContent)
    return classCommentList

def createClassCommentMap(typesHeaders):
    classMap = []
    for item in typesHeaders:
        if False == ('.hpp' in item[1]):
            typesHeader = os.path.join(item[0], item[1])
            classMap.extend(createClassCommentsForFiles(typesHeader))
    sortedMap = sorted(classMap, key=attrgetter('className'))
    #sortedMap = sorted(cppCommentMap, key=attrgetter('className', 'functionName')) 
    return sortedMap
 
def getSublistForClass(sortedMap, className):
    sublist = []
    for item in sortedMap:
        if (className == item.className):
            sublist.append(item)
    return sublist

class commentToAdd:
    def __init__(self, lineNumber, comment):
        self.lineNumber = lineNumber
        self.comment = comment
    def __repr__(self):
        return repr((self.lineNumber, self.comment))
    
class lineClassFunction:
    def __init__(self, lineNumber, className, functionName, argumentsList):
        self.lineNumber = lineNumber
        self.className = className
        self.functionName = functionName
        self.argumentsList = argumentsList
    def __repr__(self):
        return repr((self.lineNumber, self.className, self.functionName, self.argumentsList))
    
def findCommentInFunctionList(function, classFunctionList):
    if (function == 'isValid'):
        comment = '/**\n * Check if this is a valid ' + classFunctionList[0].className + \
        ' object.\n *\n * @return  Status True if object is valid, false otherwise.\n */\n'
        return comment
    if ('getDerivedId' in function):
        comment = '/**\n * Return the C handle of the derived ' + classFunctionList[0].className + \
        ' object.\n *\n * @return  C handle of the derived ' + classFunctionList[0].className + \
        ' if this objects is valid, 0 otherwise.\n */\n'
        return comment
    if (function == 'getId'):
        comment = '/**\n * Return the C handle of the ' + classFunctionList[0].className + \
        ' object.\n *\n * @return  C handle of ' + classFunctionList[0].className + \
        ' if this objects is valid, 0 otherwise.\n */\n'
        return comment
    for item in classFunctionList:
        if (item.functionName ==  function):
            return item.comments
    return ''

def correctCommentBlockArguments(comment, lineClassFunction):
    argumentsList = lineClassFunction.argumentsList
    updatedComment = comment
    if len(argumentsList) > 0:
        secondaryArgument = re.split('@param ', comment)
        numberOfParam = len(secondaryArgument) - 1
        i = 1
        while numberOfParam > 0 and i < numberOfParam + 1:
            argumentName = re.split(' ', secondaryArgument[i])
            j = 0
            if len(argumentName) > 0 and len(argumentsList) >= i:
                argumentToBeReplaced = argumentName[j]
                while j < len(argumentName) and '' == argumentName[j]:
                    j = j + 1
                    argumentToBeReplaced = argumentName[j]
                updatedComment = updatedComment.replace('@param ' + argumentToBeReplaced, '@param ' + argumentsList[i -1])
            i = i + 1
    return updatedComment

def addIndentationToCommandBlock(updateComment, indentation):
    returnComment = indentation + updateComment
    returnComment = returnComment.replace("\n", "\n"+indentation)
    k = len(returnComment)
    returnComment = returnComment[:k-len(indentation)]
    return returnComment

def createLineCommentsBlock(sortedMap, lineClassFunctionList):
    sortedPairs= sorted(lineClassFunctionList, key=attrgetter('functionName'))
    currentClassName = ''
    currentClassSubList = []
    lineCommentList = []
    
    for lineClassFunction in sortedPairs:
        if currentClassName != lineClassFunction.className:
            currentClassName = lineClassFunction.className
            currentClassSubList = getSublistForClass(sortedMap, lineClassFunction.className)
        if (len(currentClassSubList) > 0):         
            comment = findCommentInFunctionList(lineClassFunction.functionName, currentClassSubList)
            if len(comment) > 0:
                updateComment = correctCommentBlockArguments(comment, lineClassFunction)
                updateComment = addIndentationToCommandBlock(updateComment, '\t')
                #updateComment = comment
                lineCommentList.append(commentToAdd(lineClassFunction.lineNumber, updateComment))
            else:
                global methodNotFoundList
                methodNotFoundList.append(currentClassName + '  ' + lineClassFunction.functionName + '\n')
    return lineCommentList

def getArgumentsList(hppHeaderContent, lineNumber):
    argumentsList = []
    fullMethod = ''
    currentLineNumber = lineNumber
    fullMethod = hppHeaderContent[currentLineNumber]
    
    while (False == (')' in fullMethod)):
        fullMethod = fullMethod + hppHeaderContent[currentLineNumber + 1]
        currentLineNumber = currentLineNumber + 1
    fullMethod = fullMethod.replace('\n', '')
    argumentsString = re.findall('\(([^$]*)\)', fullMethod)[0]
    if len(argumentsString) > 0: 
        tempArguments = re.split(',', argumentsString)
        for tempArgument in tempArguments:
            argumentBreakDown =  re.split('\s', tempArgument)
            length = len(argumentBreakDown)
            if length > 0:
                argumentName = argumentBreakDown[length - 1]
                if '*' in argumentName:
                    argumentName = argumentName.replace('*', '')
                argumentsList.append(argumentName)
    return argumentsList

def createDerivedFieldComment(currentDerivedFieldName, sortedMap):
    currentClassSubList = getSublistForClass(sortedMap, 'Fieldmodule')
    comment = findCommentInFunctionList('create'+currentDerivedFieldName, currentClassSubList)
    if comment != '': 
        briefComment = comment.replace("Creates a", '@brief A')
        briefComment = briefComment.split(".")[0] + '.\n *\n'
        fullComment =  comment.split("@")[0]+'\n */'
        fullComment = fullComment.replace("Creates a", 'A')
        fullComment =  fullComment.replace('/**\n','')
        fullComment =  fullComment.replace('*\n','')
        fullComment =  fullComment.replace('  *',' *')
        comment = briefComment + fullComment
    return comment
    

def getMethodLineCommentsToCppTuple(hppHeaderContent, classCommentMap, sortedMap):
    lineNumber = 0
    lineClassFunctionList = []
    currentClassName = ''
    hppHeaderLength = len(hppHeaderContent)
    lineCommentList = []
    while lineNumber < hppHeaderLength:
        #print line
        line = hppHeaderContent[lineNumber]
        if 'class' in line:
            if False == (';' in line):
                if ' : public ' in line:
                    currentClassName = (re.findall('class ([^$]*) : public ', line))[0]
                else:
                    currentClassName = (re.findall('class ([^$]*)\n', line))[0]
                classCommentFound = False
                for item in classCommentMap:
                    if item.className == currentClassName:
                        lineCommentList.append(commentToAdd(lineNumber, item.comments))
                        classCommentFound = True
                if False == classCommentFound and 'Field' in currentClassName:
                    #addComment = '/**\n * @brief This is a derived Field class.\n\n * ' + \
                    #    '@see Fieldmodule::create' + currentClassName + '\n\n *' + \
                    #    'The derived Field class.\n */ '
                    mineCurrentClassName = currentClassName
                    if (':' in currentClassName):
                        mineCurrentClassName = currentClassName.split(':')[0]
                    addComment = createDerivedFieldComment(mineCurrentClassName, sortedMap)
                    lineCommentList.append(commentToAdd(lineNumber, addComment))
        else:
            if (currentClassName != ''):
                if True == ('inline' in line) and False == ('(' in line):
                    line = line + hppHeaderContent[lineNumber+1]
                if (True == ('(' in line)) and (True == (' ' in line)):
                    if (True == ('::' in line) or False == (':' in line)) and ((True == ('inline' in line) and False == ('==' in line)) or 
                        ((False == ('return' in line) and (False == ('=' in line))))):
                        functionName = (re.findall('[\s]([^$]*)\(', line))
                       # print functionName
                        if len(functionName) > 0:
                            isCppMethod = False
                            if True == ('inline' in line):
                                isCppMethod = True
                            else:
                                currentLineNumber = lineNumber
                                currentLine = hppHeaderContent[currentLineNumber]
                                while False == ('{' in currentLine) and False == ('}' in currentLine):
                                    currentLineNumber = currentLineNumber + 1
                                    currentLine =  hppHeaderContent[currentLineNumber]
                                if '{' in currentLine:
                                    isCppMethod = True                                
                            if isCppMethod == True:
                                argumentsList = getArgumentsList(hppHeaderContent, lineNumber)
                                functionName =  functionName[0]
                                if '\t' in functionName:
                                    functionName = functionName.replace('\t', ' ')
                                while ' ' in functionName:
                                    functionName = (re.findall(' ([^$]*)', functionName))[0]
                                if '*' in functionName:
                                    functionName = functionName.replace('*', '')
                                lineClassFunctionList.append(lineClassFunction(lineNumber, currentClassName, functionName, argumentsList))
        lineNumber = lineNumber + 1
    lineCommentList.extend(createLineCommentsBlock(sortedMap, lineClassFunctionList))
    return lineCommentList

def getEnumCommentsForEnumString(sortedEnumMap, cEnumName):
    for item in sortedEnumMap:
        if (cEnumName in item.enumeratorName):
            return item
    return 0

def createEnumLineCommentsBlock(cEnumName, enumLineNumber, enumIndent, hppHeaderContent, sortedEnumMap, currentClassName):
    lineNumber = enumLineNumber
    line = hppHeaderContent[lineNumber]
    enumLineCommentsBlocks = []
    enumCommentsItem = getEnumCommentsForEnumString(sortedEnumMap, cEnumName)
    comments = enumCommentsItem.comments
    if len(enumIndent) > 0:
        comments = enumIndent + comments
        comments = comments.replace("\n", "\n"+enumIndent)
        comments = comments[:len(comments)-len(enumIndent)]
    enumLineCommentsBlocks.append(commentToAdd(enumLineNumber, comments))
    while False == ('}' in line):
        #if '/*' in line:
        #    print line
        if '=' in line:
            mineCommentToAdd = ''
            enumerators = re.split('=', line)
            enumerator = enumerators[1]
            cpp_enumerator = enumerators[0]
            cpp_enumerator = cpp_enumerator.replace("\n", "")
            cpp_enumerator = cpp_enumerator.replace(" ", "")
            cpp_enumerator = cpp_enumerator.replace("\t", "")
            cpp_enumerator = cpp_enumerator.replace(",", "")
            enumerator = enumerator.replace("\n", "")
            enumerator = enumerator.replace(" ", "")
            enumerator = enumerator.replace("\t", "")
            enumerator = enumerator.replace(",", "")
            for item in enumCommentsItem.enumsTuple:
              #  if 'CMZN_ELEMENT_SHAPE_TYPE' in item[0]:
              #      print  item[0]
                if item[0] == enumerator:
                    mineCommentToAdd = item[1]
                    indent = re.findall('\s+', line)
                    if len(indent) > 0:
                        mineCommentToAdd = indent[0] + mineCommentToAdd
                        mineCommentToAdd = mineCommentToAdd.replace("\n", "\n"+indent[0])
                    if (mineCommentToAdd[len(mineCommentToAdd)-1]!='\n'):
                        mineCommentToAdd = mineCommentToAdd + '\n'
                    enumLineCommentsBlocks.append(commentToAdd(lineNumber+1, mineCommentToAdd))
            cpp_enumerator =  cpp_enumerator.replace('\n','')
            global cToCppClassObjectList
            cToCppClassObjectList.append(FunctionClassObject(enumerator, currentClassName, cpp_enumerator))             
            if len(mineCommentToAdd) == 0:
                global enumeratorNotFoundList
                enumeratorNotFoundList.append(enumerator)
        lineNumber = lineNumber + 1
        line = hppHeaderContent[lineNumber]
    return enumLineCommentsBlocks
        
def getEnumLineCommentsToCppTuple(hppHeaderContent, sortedEnumMap):
    lineNumber = 0
    lineEnumList = []
    currentClassName = ''
    contentLength = len(hppHeaderContent)
    while lineNumber < contentLength:
        #print line
        line = hppHeaderContent[lineNumber]
        if 'class' in line:
            if False == (';' in line):
                if ' : public ' in line:
                    currentClassName = (re.findall('class ([^$]*) : public ', line))[0]
                else:
                    currentClassName = (re.findall('class ([^$]*)\n', line))[0]
        else:
            if ((currentClassName != '') and ((True == ('enum' in line)) and (False == ('(' in line))))\
                or (True == ('enum Status' in line)) or (True == ('enum Scenecoordinatesystem\n' in line)):
                    enumName = (re.findall('enum ([^$]*)', line))
                    if len(enumName) > 0:
                        enumName = enumName[0]
                        cEnumName = currentClassName+enumName
                        charPos = 0
                        while charPos < len(cEnumName):
                            currentChar = cEnumName[charPos]
                            if (currentChar.isupper()):
                                newchar = currentChar.lower()
                                cEnumName = cEnumName[0:charPos] + "_" + newchar+ cEnumName[charPos+1:]
                            charPos = charPos + 1
                        cEnumName = "cmzn" + cEnumName
                        cEnumName = cEnumName.replace("\n", "")
                        cEnumName = cEnumName.replace(" ", "")
                        enumLineNumber = lineNumber
                        enumIndent = re.findall('\s+', line)
                        enumName =  enumName.replace('\n','')
                        global cToCppClassObjectList
                        cToCppClassObjectList.append(FunctionClassObject(cEnumName, currentClassName, enumName))
                        if (len(enumIndent) > 0):
                            enumIndent = enumIndent[0]
                        else:
                            enumIndent = ''
                        lineEnumList.extend(createEnumLineCommentsBlock(cEnumName, enumLineNumber, enumIndent, hppHeaderContent, sortedEnumMap, currentClassName))
        lineNumber = lineNumber + 1
    return lineEnumList

def removeEnumCommentsFromCpp(hppHeaderContent):
    lineNumber = 0
    newHeader = hppHeaderContent
    contentLength = len(newHeader)
    while lineNumber < contentLength:
        line = newHeader[lineNumber]
        if (True == ('enum' in line)) and (False == ('(' in line)):
            newLineNumber = lineNumber - 1
            currentLineContent = newHeader[newLineNumber]
            if ('*/' in currentLineContent):
                while False == ('/*' in currentLineContent):
                    del newHeader[newLineNumber]
                    newLineNumber = newLineNumber -1
                    currentLineContent = newHeader[newLineNumber]
                    lineNumber = lineNumber - 1
                del newHeader[newLineNumber]
            lineNumber = lineNumber + 1
            currentLineContent = newHeader[lineNumber]
            if '{' in currentLineContent:
                while False == ('}' in  currentLineContent):
                    commentPos = currentLineContent.find('/*')
                    if commentPos > - 1:
                        comPos = currentLineContent.find(',')
                        if comPos > -1 and commentPos > comPos:
                            validLine = currentLineContent[:comPos+1] + '\n'
                        else:
                            validLine = currentLineContent[:commentPos] + '\n'
                        newHeader[lineNumber] = validLine
                        if False == ('*/' in currentLineContent):
                             lineNumber = lineNumber + 1
                             currentLineContent = newHeader[lineNumber]
                             while False == ('*/' in currentLineContent):
                                 newHeader[lineNumber] = ''
                                 lineNumber = lineNumber + 1
                                 currentLineContent = newHeader[lineNumber]
                             newHeader[lineNumber] = ''
                    lineNumber = lineNumber + 1
                    currentLineContent = newHeader[lineNumber]
        contentLength = len(newHeader)
        lineNumber = lineNumber + 1
    return newHeader

def postProcessCommentString(comment):
    processedComment = comment
    if '@see' in processedComment and False == ( 'Fieldmodule::' in processedComment):
        splitString = processedComment.split('@see ')
        length = len(splitString)
        if length > 0:
            index = 1
            while index < length:
                functionName = splitString[index]
                functionName = functionName.split('\n')[0]
                functionName = functionName.split(' ')[0]
                if '.' in functionName:
                    functionName = functionName.replace('.', '')
                listLength = len(cToCppClassObjectList)
                i = 0
                commentFound = False
                while (i < listLength) and (False == commentFound):
                    item = cToCppClassObjectList[i]
                    if item.function ==  functionName:
                        commentFound = True
                        cppString = item.className + '::'+ item.object
                        processedComment = processedComment.replace(functionName, cppString)
                    i = i + 1
                if (commentFound == False) and ('_id' in functionName):
                    cppString = cToCppName(functionName)
                    processedComment = processedComment.replace(functionName, cppString)
                    commentFound = True
                if (commentFound == False):
                    global seeAlsoNotFoundList
                    seeAlsoNotFoundList.append(functionName)
                index = index + 1
        #functionName = re.findall('@see ([^$]*)', processedComment)[0]
        #while '\s' in functionName:
        #    functionName = re.findall('([^$]*)\s', functionName)[0]
    processedComment = processedComment.replace('CMZN_OK', 'OpenCMISS::Zinc::OK')
    processedComment = processedComment.replace('CMZN_ERROR_ARGUMENT', 'OpenCMISS::Zinc::ERROR_ARGUMENT')
    processedComment = processedComment.replace('CMZN_ERROR_MEMORY', 'OpenCMISS::Zinc::ERROR_MEMORY')
    processedComment = processedComment.replace('CMZN_ERROR_GENERAL', 'OpenCMISS::Zinc::ERROR_GENERAL')
    return processedComment

def createNewCppFile(hppFolderName, hppFileName, classCommentMap, sortedMap, sortedEnumMap):
    hppHeaderContent = []
    hppHeader = os.path.join(hppFolderName, hppFileName)
    with open(hppHeader) as f:
        hppHeaderContent = f.readlines()
    enumCommentRemovedHeader = removeEnumCommentsFromCpp(hppHeaderContent)
    lineCommentList = getMethodLineCommentsToCppTuple(enumCommentRemovedHeader, classCommentMap, sortedMap)
    lineCommentList.extend(getEnumLineCommentsToCppTuple(enumCommentRemovedHeader, sortedEnumMap))
    if (len(lineCommentList) > 0):
        sortedList = sorted(lineCommentList, key=attrgetter('lineNumber'), reverse=True)
        for lineComment in sortedList:
            commentString = postProcessCommentString(lineComment.comment)
            enumCommentRemovedHeader.insert(lineComment.lineNumber, commentString)
    outputFile = open(targe_dir+'/'+hppFileName, 'w')
    for outputLine in enumCommentRemovedHeader:
        outputFile.write(outputLine)
    outputFile.close()
      
def createAllCppFiles(hppFilenames, classCommentMap, sortedMap, sortedEnumMap):
    for item in hppFilenames:
        createNewCppFile(item[0], item[1], classCommentMap, sortedMap, sortedEnumMap)
    #createNewCppFile(file_pairs[0][0][0], file_pairs[0][0][1], sortedMap)
    return True

def printDebugMessage():
    if len(enumeratorNotFoundList) > 0:
        print '***Following enumerator not found***'
        for enumerator in enumeratorNotFoundList:
            print enumerator
    if len(methodNotFoundList) > 0:
        print '***Following methods not found***'
        for method in methodNotFoundList:
            print method
    if len(seeAlsoNotFoundList) > 0:
        print '***Following @see function not found***'
        for seeAlso in seeAlsoNotFoundList:
            print seeAlso

def main():
    hFilenames, hppFilenames, typesFilenames = getFilename()
  #  summary(hFilenames, hppFilenames, typesFilenames)
    file_pairs = match_pair(hFilenames, hppFilenames, typesFilenames)
    hppFilenames.append(['./core/source/api/zinc/types', 'scenecoordinatesystem.hpp'])
    typesFilenames.append(['./core/source/api/zinc', 'status.h'])
  #  for pair in pair_list:
  #      print pair;
    try:
	os.makedirs(targe_dir)
	print "creating "+ targe_dir + " folder"
    except OSError:
	print "targe_dir already exists"
    sortedMap = createCFunctionCommentMap(hFilenames)
    classCommentMap = createClassCommentMap(typesFilenames)
    sortedEnumMap = createEnumMap(typesFilenames)
  #  for item in sortedMap:
  #      print item.className, item.functionName
    createAllCppFiles(hppFilenames, classCommentMap, sortedMap, sortedEnumMap)
    if globalSummary:
        printDebugMessage()
        
main()
