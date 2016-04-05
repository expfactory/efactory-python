'''
survey.py: part of expfactory package
Functions to work with javascript surveys

'''

from expfactory.experiment import get_experiments
from glob import glob
import pandas
import json
import uuid
import re
import os

def get_surveys(survey_repo=None,load=False,warning=True,repo_type="surveys"):
    '''get_surveys is a wrapper for "get_experiments" - the functionality is the same, but provided for users: return loaded json for all valid survyes from an surveys folder
    :param survey_repo: full path to the surveys repo
    :param load: if True, returns a list of loaded config.json objects. If False (default) returns the paths to the experiments
    :param repo_type: tells the user what kind of task is being parsed, default is "experiments," but can also be "surveys" when called by get_surveys
    '''
    return get_experiments(experiment_repo=survey_repo,load=load,warning=warning,repo_type=repo_type)


def get_question_types():
   '''get_question_types returns a list of possible question types
   '''
   return ["radio","checkbox","textfield","textarea","numeric","table","instruction"]


# CREATION FUNCTIONS ##############################################################################

def create_instruction(text,id_attribute,tag="h2"):
    '''create_instruction creates a tag of type [tag] with some text inside, useful for description or instructions.
    :param text: the text to give in the instruction.
    :param id_attribute: the unique id for the question
    :param tag: the html tag for the instruction (eg, p or h2)
    '''
    return "<%s>%s</%s><br><br><br><br>" %(tag,text,tag)


def format_options_values(options,values):
    if isinstance(options,str):
        options = [options]
    if isinstance(values,str):
        values = [values]
    return options,values

def get_required_string(required_int):
    required = ""
    if required_int == 1:
        required = "required"
    return required

def parse_meta(text,options=None):
    '''parse_meta returns fields to include in inputs for question text and options, for export
    :param text: the text of the question (required)
    :param options: options to include with the data (optional)
    '''
    text = text.replace('"',"'")
    if options!= None:
        options_joined =  "|".join([x.replace('"',"'") for x in options])
        return 'meta-options="%s" meta-text="%s"' %(options_joined,text)
    return 'meta-text="%s"' %(text)


def add_classes(classes,new_classes):
    '''add_classess adds a string of new classes to current, if defined
    :param classes: string of current classes, must be defined
    :param new_classes: new classes to add, optional
    '''
    if new_classes != None:
        classes = "%s %s" %(classes,new_classes)
    return classes

def create_radio(text,id_attribute,options,values,classes="",required=0):
    '''create_radio generate a material lite radio button given a text field, and a set of options.
    :param text: The text (content) of the question to ask
    :param id_attribute: the unique id for the question
    :param options: a list of text options for the user to select from (not the value of the field)
    :param values: a list of values for corresponding options
    :param classes: classes to add to the default, should be a string
    :param required: is the question required? 0=False,1=True, default 0
    ''' 
    class_names = "mdl-radio mdl-js-radio mdl-js-ripple-effect"       

    options,values = format_options_values(options,values)
    
    required = get_required_string(required)

    meta = parse_meta(text,options)

    if len(options) == len(values):
        radio_html = '<p id="%s_options">%s</p>' %(id_attribute,text)
        for n in range(len(options)):
            option_id = "%s_%s" %(id_attribute,n)
            radio_html = '%s\n<label class="%s" for="option-%s">\n<input type="radio" id="option-%s" class="mdl-radio__button %s %s" name="%s_options" value="%s" %s>\n<span class="mdl-radio__label">%s</span>\n</label>' %(radio_html,class_names,option_id,option_id,required,classes,id_attribute,values[n],meta,options[n])
        return "%s<br><br><br><br>" %(radio_html)
        
    print "ERROR: %s options provided, and only %s values. Must define one option per value." %(len(options),len(values))
    return ""

def create_checkbox(text,id_attribute,options,classes="",required=0):
    '''create_checkbox generate a material lite checkbox field given a text field, and a set of options.
    :param text: The text (content) of the question to ask
    :param options: a list of text options for the user to select from
    :param id_attribute: the unique id for the question
    :param classes: additional classes to add to the input, should be a string
    :param required: is the question required? 0=False,1=True, default 0
    '''        
    class_names = "mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect"

    required = get_required_string(required)

    meta = parse_meta(text,options)

    checkbox_html = '<p id="%s_options">%s</p>' %(id_attribute,text)
    for n in range(len(options)):
        option_id = "%s_%s" %(id_attribute,n)
        checkbox_html = '%s\n<label class="%s" for="checkbox-%s">\n<input type="checkbox" id="checkbox-%s" %s class="mdl-checkbox__input %s %s" name="%s_options">\n<span class="mdl-checkbox__label">%s</span>\n</label>' %(checkbox_html,class_names,option_id,option_id,meta,classes,required,id_attribute,options[n])
    return "%s<br><br><br>" %(checkbox_html)
    
def base_textfield(text,id_attribute,box_text=None):
    '''format_textfield parses input for a general textfield, returning base html, box_text, and id.
    :param text: Any text content to precede the question field (default is None)
    :param id_attribute: the unique id for the question
    :param box_text: text content to go inside the box (default is None)
    '''        
    if box_text == None:
        box_text = ""

    textfield_html = ""
    if text != None:
        textfield_html = '<p id="%s">%s</p>' %(id_attribute,text)

    return textfield_html,box_text


def create_textfield(text,id_attribute,box_text=None,classes="",required=0):
    '''create_textfield generates a material lite text field given a text prompt.
    :param text: Any text content to precede the question field (default is None)
    :param id_attribute: the unique id for the question
    :param box_text: text content to go inside the box (default is None)
    :param classes: additional classes to add to the input, should be a string
    :param required: is the question required? 0=False,1=True, default 0
    '''   
    class_names = "mdl-textfield mdl-js-textfield"

    textfield_html,box_text = base_textfield(text,id_attribute,box_text)
    required = get_required_string(required)
    meta = parse_meta(text)

    return '%s\n<div class="%s">\n<input class="mdl-textfield__input %s %s" name="%s" type="text" id="%s" %s>\n<label class="mdl-textfield__label" for="%s">%s</label>\n</div><br><br><br>' %(textfield_html,class_names,classes,required,id_attribute,id_attribute,meta,id_attribute,box_text)


def create_numeric_textfield(text,id_attribute,box_text=None,classes="",required=0):
    '''create_numeric generates a material lite numeric text field given a text prompt.
    :param text: Any text content to precede the question field (default is None)
    :param id_attribute: the unique id for the question
    :param box_text: text content to go inside the box (default is None)
    :param id_attribute: an id to match to the text field
    :param classes: classes to add to the input. Must be a string.
    :param required: is the question required? 0=False,1=True, default 0
    '''   
    class_names = "mdl-textfield mdl-js-textfield"  

    required = get_required_string(required)
    textfield_html,box_text = base_textfield(text,id_attribute,box_text)
    meta = parse_meta(text)

    return '%s\n<div class="%s">\n<input class="mdl-textfield__input %s %s" type="number" id="%s" name="%s" %s>\n<label class="mdl-textfield__label" for="%s">%s</label>\n<span class="mdl-textfield__error">Input is not a number!</span>\n</div><br><br><br>' %(textfield_html,class_names,classes,required,id_attribute,id_attribute,meta,id_attribute,box_text)


def create_select_table(text,id_attribute,df,classes="",required=0):
    '''create_select_table generates a material lite table from a pandas data frame.
    :param df: A pandas data frame, with column names corresponding to columns, and rows
    :param id_attribute: the unique id for the question
    :param text: A text prompt to put before the table
    :param classes: the classes to apply to the input. If none, default will be used.
    :param required: is the question required? 0=False,1=True, default 0
    '''        
    if isinstance(df,pandas.DataFrame):
    
        
        class_names = "mdl-data-table mdl-js-data-table mdl-data-table--selectable mdl-shadow--2dp %s" %(required)

        required = get_required_string(required)
        table_html = '<p>%s</p>\n<table id="%s" class="%s %s">\n<thead>\n<tr>' %(text,id_attribute,class_names,classes)
        meta = parse_meta(text)

        # Parse column names
        column_names = df.columns.tolist()
        for column_name in columns_names:
            table_html = '%s\n<th class="mdl-data-table__cell--non-numeric">%s</th>' %(table_html,column_name)
        table_html = "%s\n</tr>\n</thead>\n<tbody>" %(table_html)

        # Parse rows
        for row in df.iterrows():
            row_id = row[0]
            table_html = "%s\n<tr>" %(table_html)
            values = row[1].tolist()
            for value in values:
                if isinstance(value,str) or isinstance(value,unicode):
                    table_html = '%s\n<td class="mdl-data-table__cell--non-numeric">%s</td>' %(table_html,str(value))
                else:
                    table_html = '%s\n<td>%s</td>' %(table_html,value)
            table_html = "%s\n</tr>" %(table_html)
        return "%s\n</tbody>\n</table><br><br><br>" %(table_html)
 
    print "ERROR: DataFrame (df) must be a pandas.DataFrame"


def create_textarea(text,id_attribute,classes="",rows=3,required=0):
    '''create_textarea generates a material lite multi line text field with a text prompt.
    :param text: A text prompt to put before the text field
    :param id_attribute: the unique id for the question
    :param classes: classes to add to the text field (optional) should be string.
    :param rows: number of rows to include in text field (default 3)
    :param required: is the question required? 0=False,1=True, default 0
    '''        
    textfield_html,box_text = base_textfield(text,id_attribute,box_text)
    meta = parse_meta(text)

    class_names = "mdl-textfield mdl-js-textfield"

    return '%s\n<div class="%s"><textarea class="mdl-textfield__input %s %s" type="text" rows="%s" id="%s" name="%s" %s ></textarea>\n<label class="mdl-textfield__label" for="%s">%s</label></div><br><br><br>' %(textfield_html,class_names,classes,required,rows,id_attribute,id_attribute,meta,id_attribute,box_text)


# EXPORT FUNCTIONS ##############################################################################

def export_instruction(text,id_attribute,required=0):
    return {"text":text,"id":id_attribute,"required":required}

def export_radio(text,id_attribute,options,values,required=0):
    '''export_radio returns a json data structure of the question
    :param text: The text (content) of the question to ask
    :param id_attribute: the unique id for the question
    :param options: a list of text options for the user to select from (not the value of the field)
    :param values: a list of values for corresponding options
    :param required: is the question required? 0=False,1=True, default 0
    ''' 
    options,values = format_options_values(options,values)    
    question_list = {}

    if len(options) == len(values):
        question_list["id"] = "%s_options" %(id_attribute)
        question_list["required"] = required
        question_list["text"] = text
        option_list = []
        for n in range(len(options)):
            option_id = "%s_%s" %(id_attribute,n)
            option_list.append({"id":option_id,"value":values[n],"text":options[n]})
        question_list["options"] = option_list
    return question_list

def export_checkbox(text,id_attribute,options,required=0):
    '''export_checkbox returns json data structure to describe checkbox
    :param text: The text (content) of the question to ask
    :param options: a list of text options for the user to select from
    :param id_attribute: the unique id for the question
    :param required: is the question required? 0=False,1=True, default 0
    '''        
    question_list = {}
    question_list["id"] = "%s_options" %(id_attribute)
    question_list["required"] = required
    question_list["text"] = text
    option_list = []
    for n in range(len(options)):
        option_id = "%s_%s" %(id_attribute,n)
        option_list.append({"id":option_id,"text":options[n]})
    question_list["options"] = option_list
    return question_list


def export_textfield(text,id_attribute,required=0):
    '''create_textfield generates a material lite text field given a text prompt.
    :param text: Any text content to precede the question field (default is None)
    :param id_attribute: the unique id for the question
    :param required: is the question required? 0=False,1=True, default 0
    '''   
    question_list = {}
    question_list["id"] = id_attribute
    question_list["required"] = required
    question_list["text"] = text
    return question_list


# PARSING FUNCTIONS ############################################################################

def parse_validation(required_counts):
    '''parse_validation parses code to validate each step
    :param page_count: the total number of pages for the survey (called "steps")
    :param question_counts: 
    '''
    validation = ""
    current_page = 1
    pages = required_counts.keys()
    pages.sort()
    for page_number in pages:
        required_questions = required_counts[page_number]
        if current_page == 1:
            validation = "%s if ( state.stepIndex === %s ) {\n" %(validation,page_number)
        else:
            validation = "%s else if ( state.stepIndex === %s ) {\n" %(validation,page_number)
        validation = '%s if (($(".page%s.required:checked").length + $(".page%s.required:text").filter(function() { return $(this).val();}).length) != %s){\nis_required($(".page%s.required:not(checked)"));\nreturn false;\n' %(validation,page_number,page_number,required_questions,page_number)
        # If we are at the last page, passing validation should enable the submit
        if page_number == pages[-1]:
            validation = '%s } else {\nexpfactory_finished=true;\n' %(validation)
        validation = '%s}}' %(validation)
        current_page+=1

    return validation


def read_survey_file(question_file,delim="\t"):
    ''''read_survey_file reads in a survey file, and returns a DataFrame with columns. If there is an error, None is returned, and the error is printed to the screen.
    :param question_file: the survey.tsv (or other) questions file
    :param delim: the delimiter of the question_file
    '''
    df = pandas.read_csv(question_file,sep=delim)
    required_columns = ["question_type","question_text","page_number","option_text","option_values","required"]
    optional_columns = ["variables"]
    acceptable_types = get_question_types()

    # Parse column names, ensure lower case, check that are valid
    column_names = [x.lower() for x in df.columns.tolist()]
    acceptable_columns = []
    for column_name in column_names:
        if column_name in required_columns + optional_columns:
            acceptable_columns.append(column_name)

    # Make sure all required columns are included
    if len([x for x in required_columns if x in acceptable_columns]) == len(required_columns):
        df.columns = acceptable_columns
        return df
    else:
        missing_columns = [x for x in required_columns if x not in acceptable_columns]
        print "Question file is missing required columns %s" %(",".join(missing_columns))
        return None

def parse_questions(question_file,exp_id,delim="\t",return_requiredcount=True):
    '''parse_questions reads in a text file, separated by delim, into a pandas data frame, checking that all column names are provided.
    :param question_file: a TAB separated file to be read with experiment questions. Will also be validated for columns names.
    :param exp_id: the experiment unique id, to be used to generate question ids
    :param return_requiredcount: if True, will return questions,page_count where page_count is a dictionary to look up the number of required questions on each page {1:10}
    '''
    df = read_survey_file(question_file,delim=delim)
    acceptable_types = get_question_types()
    required_counts = dict()

    if isinstance(df,pandas.DataFrame):
 
        # Each question will have id [exp_id][question_count] with appended _[count] for options
        question_count = 0
        questions = []
        current_page_number = 1
        current_page = '<div class="step">'
        for question in df.iterrows():

            question_type = question[1].question_type
            question_text = question[1].question_text
            page_number = question[1].page_number
            page_class = "page%s" %(page_number)
            options = question[1].option_text
            values = question[1].option_values
            required = int(question[1].required)
            unique_id = "%s_%s" %(exp_id,question_count)
            new_question = None
            if required == 1:
                if page_number not in required_counts:
                    required_counts[page_number] = 1
                else:
                    required_counts[page_number] = required_counts[page_number] + 1

            if question_type in acceptable_types:

                # Instruction block / text
                if question_type == "instruction":
                    new_question = create_instruction(question_text,tag="h3",id_attribute=unique_id)
                
                # Radio button
                elif question_type == "radio":
                    if not str(options) == "nan" and not str(values) == "nan":
                        new_question = create_radio(text=question_text,
                                                    options=options.split(","),
                                                    values = values.split(","),
                                                    required=required,
                                                    id_attribute=unique_id,
                                                    classes=page_class)
                    else:
                        print "Radio question %s found null for options or values, skipping." %(question_text)
 
                # Checkbox
                elif question_type == "checkbox":
                    if not str(options) == "nan":
                        new_question = create_checkbox(text=question_text,
                                                       options=options.split(","),
                                                       required=required,
                                                       id_attribute=unique_id,
                                                       classes=page_class)
                    else:
                        print "Checkbox question %s found null for options, skipping." %(question_text)

                # Textareas and Textfields, regular and numeric
                elif question_type == "textarea":
                    new_question = create_textarea(question_text,
                                                   required=required,
                                                   id_attribute=unique_id,
                                                   classes=page_class)

                elif question_type == "textfield":
                    new_question = create_textfield(question_text,
                                                    required=required,
                                                    id_attribute=unique_id,
                                                    classes=page_class)

                elif question_type == "numeric":
                    new_question = create_numeric_textfield(question_text,
                                                            required=required,
                                                            id_attribute=unique_id,
                                                            classes=page_class)


                # Table
                elif question_type == "table":
                    print "Table option not yet supported! Coming soon."
 
                question_count+=1
            
            if new_question != None:
                # Add the new question to the current page
                if page_number == current_page_number:                 
                    current_page = "%s\n%s" %(current_page,new_question)
                # Save the current page, add the current question to the next page
                else:
                    questions.append("%s</div>" %current_page)
                    current_page = '<div class="step">\n%s' %new_question
                    current_page_number = page_number

        # Add the last page
        questions.append("%s</div>" %current_page)

        if return_requiredcount == True:
            return questions,required_counts
        return questions
    else:
        return None


def generate_survey(experiment,experiment_folder,form_action="#",classes=None,survey_file="survey.tsv",get_validation=True,csrf_token=False):
    '''generate_survey takes a list of questions and outputs html for an expfactory survey, and validation code
    :param experiment: The experiment loaded config.json
    :param experiment_folder: should contain survey.tsv, a TAB separated file with question data. Will be read into a pandas data frame, and columns must follow expfactory standard. Data within columns is separated by commas.
    :param form_action: the form action to take at the bottom of the page
    :param classes: the classes to apply to the outer content div. If none, default will be used
    :param survey_file: the survey file, should be survey.tsv for a valid survey experiment
    :param get_validation: get code for validation, default is True
    :param csrf_token: if true, include django code for csrf_token ({% csrf_token %})
    '''       
    if classes == None:
        classes = "experiment-layout mdl-layout mdl-layout--fixed-header mdl-js-layout mdl-color--grey-100"

    # We will generate unique ids for questions based on the exp_id
    exp_id = experiment[0]["exp_id"]
    question_file = "%s/%s" %(experiment_folder,survey_file)

    questions,required_count = parse_questions(question_file,exp_id=exp_id)

    # Get validation code based on maximum page value
    validation = parse_validation(required_count)
    token = ""
    if csrf_token == True:
        token = "{% csrf_token %}"

    if questions != None:
        survey = '<div class="%s">\n<div class="experiment-ribbon"></div>\n<main class="experiment-main mdl-layout__content">\n<div class="experiment-container mdl-grid">\n<div class="mdl-cell mdl-cell--2-col mdl-cell--hide-tablet mdl-cell--hide-phone">\n</div>\n<div class="experiment-content mdl-color--white mdl-shadow--4dp content mdl-color-text--grey-800 mdl-cell mdl-cell--8-col">\n\n<div id="questions">\n\n<form name="questions" action="%s", method="POST">%s' %(classes,form_action,token)

        for question in questions:
            survey = "%s\n%s" %(survey,question)       
        if get_validation == True:
            return survey,validation    
        return survey
    else:
        print "ERROR: parsing input text file survey.tsv. Will not generate survey HTML"


def export_questions(experiment,experiment_folder,survey_file="survey.tsv",delim="\t"):
    '''export_questions reads in a text file, separated by delim, and returns a json data structure with questions to look up
    :param question_file: a TAB separated file to be read with experiment questions. Will also be validated for columns names.
    :param exp_id: the experiment unique id, to be used to generate question ids
    :param experiment_folder: should contain survey.tsv, a TAB separated file with question data. Will be read into a pandas data frame, and columns must follow expfactory standard. Data within columns is separated by commas.
    :param survey_file: the survey file, should be survey.tsv for a valid survey experiment
    '''
    exp_id = experiment[0]["exp_id"]
    question_file = "%s/%s" %(experiment_folder,survey_file)
    df = read_survey_file(question_file,delim=delim)
    acceptable_types = get_question_types()

    if isinstance(df,pandas.DataFrame):
 
        # Each question will have id [exp_id][question_count] with appended _[count] for options
        question_count = 0
        questions = dict()
        for question in df.iterrows():

            question_type = question[1].question_type
            question_text = question[1].question_text
            page_number = question[1].page_number
            page_class = "page%s" %(page_number)
            options = question[1].option_text
            values = question[1].option_values
            required = int(question[1].required)
            unique_id = "%s_%s" %(exp_id,question_count)
            new_question = None

            if question_type in acceptable_types:

                # Instruction block / text
                if question_type == "instruction":
                    new_question = export_instruction(question_text,
                                                      id_attribute=unique_id,
                                                      required=required)
                
                # Radio button
                elif question_type == "radio":
                    if not str(options) == "nan" and not str(values) == "nan":
                        new_question = export_radio(text=question_text,
                                                    options=options.split(","),
                                                    values = values.split(","),
                                                    required=required,
                                                    id_attribute=unique_id)
                    else:
                        print "Radio question %s found null for options or values, skipping." %(question_text)
 
                # Checkbox
                elif question_type == "checkbox":
                    if not str(options) == "nan":
                        new_question = export_checkbox(text=question_text,
                                                       options=options.split(","),
                                                       required=required,
                                                       id_attribute=unique_id)
                    else:
                        print "Checkbox question %s found null for options, skipping." %(question_text)

                # Textareas and Textfields, regular and numeric
                elif question_type in ["textarea","textfield","numeric"]:
                    new_question = export_textfield(question_text,
                                                   required=required,
                                                   id_attribute=unique_id)
 
                question_count+=1
                questions[new_question["id"]] = new_question

        return questions
    else:
        return None
