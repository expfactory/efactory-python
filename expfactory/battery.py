'''
battery.py: part of expfactory package
Functions to generate batteries

'''
from expfactory.vm import custom_battery_download, get_jspsych_init, get_stylejs
from expfactory.experiment import get_experiments, load_experiment
from expfactory.utils import copy_directory, get_template, \
     sub_template, get_installdir, save_template
import tempfile
import shutil
import uuid
import os
import re


def generate_base(battery_dest,tasks=None,experiment_repo=None,survey_repo=None,game_repo=None,
                  battery_repo=None,warning=True):
    '''generate_base returns a folder with downloaded experiments, surveys, and battery, either specified by the user or a temporary directory, to be used by generate_local and generate (for psiturk)
    :param battery_dest: [required] is the output folder for your battery. This folder MUST NOT EXIST.
    :param battery_repo: location of psiturk-battery repo to use as a template. If not specified, will be downloaded to a temporary directory
    :param experiment_repo: location of a expfactory-experiments repo to check for valid experiments. If not specified, will be downloaded to a temporary directory
    :param survey_repo: location of a expfactory-surveys repo to check for valid surveys. If not specified, will be downloaded to a temporary directory
    :param tasks: a list of experiments and surveys, meaning the "exp_id" variable in the config.json, to include. This variable also conincides with the tasks folder name.
    :param warning: show warnings when validating experiments (default True)
    '''
    repos = []
    tmpdir = None
    if battery_repo == None:
        tmpdir = custom_battery_download(repos=['battery'])
        battery_repo = "%s/battery" %(tmpdir) 
    if experiment_repo == None and survey_repo == None and game_repo == None:
        tmpdir = custom_battery_download(tmpdir, ['experiments', 'surveys', 'games'])
        experiment_repo = "%s/experiments" %(tmpdir)      
        survey_repo = "%s/surveys" %(tmpdir)     
        game_repo = "%s/games" %(tmpdir)     


    # Copy battery skeleton to destination
    copy_directory(battery_repo,battery_dest)
    valid_experiments = []
    valid_surveys = []
    valid_games = []
    if experiment_repo is not None:
        valid_experiments = get_experiments(experiment_repo,warning=warning)
    if survey_repo is not None:
        valid_surveys = get_experiments(survey_repo,warning=warning,repo_type="surveys")
    if game_repo is not None:
        valid_games = get_experiments(game_repo,warning=warning,repo_type="games")
    # If the user wants to select a subset
    if tasks != None:
        valid_experiments = [x for x in valid_experiments if os.path.basename(x) in [os.path.basename(e) for e in tasks]]
        valid_surveys = [x for x in valid_surveys if os.path.basename(x) in [os.path.basename(e) for e in tasks]]
        valid_games = [x for x in valid_games if os.path.basename(x) in [os.path.basename(e) for e in tasks]]

    base = {"battery_repo":battery_repo,
           "experiment_repo":experiment_repo,
           "survey_repo":survey_repo,
           "game_repo":game_repo,
           "experiments":valid_experiments,
           "surveys":valid_surveys,
           "games":valid_games}        

    return base

def generate_local(battery_dest=None,subject_id=None,battery_repo=None,experiment_repo=None,experiments=None,warning=True,time=30):
    '''generate_local deploys a local battery
    will create a battery from a template and list of experiments
    :param battery_dest: is the output folder for your battery. This folder MUST NOT EXIST. If not specified, a temp directory will be used
    :param battery_repo: location of psiturk-battery repo to use as a template. If not specified, will be downloaded to a temporary directory
    :param experiment_repo: location of a expfactory-experiments repo to check for valid experiments. If not specified, will be downloaded to a temporary directory
    :param experiments: a list of experiments, meaning the "exp_id" variable in the config.json, to include. This variable also conincides with the experiment folder name.
    :param subject_id: The subject id to embed in the experiment, and the name of the results file. If none is provided, a unique ID will be generated.
    :param time: Maximum amount of time for battery to endure, to select experiments
    '''
    if battery_dest == None:
        battery_dest = tempfile.mkdtemp()
        shutil.rmtree(battery_dest)

    # We can only generate a battery to a folder that does not exist, to be safe
    if not os.path.exists(battery_dest):
        base = generate_base(battery_dest=battery_dest,
                             tasks=experiments,
                             experiment_repo=experiment_repo,
                             battery_repo=battery_repo,
                             warning=warning)
        # We will output a local battery template (without psiturk) 
        template_exp = "%s/templates/localbattery.html" %get_installdir()
        template_exp_output = "%s/index.html" %(battery_dest)
       
        # Generate a unique id
        if subject_id == None:
            subject_id = uuid.uuid4()

        # Add custom variable "subject ID" to the battery - will be added to data
        custom_variables = dict()
        custom_variables["exp"] = [("[SUB_SUBJECT_ID_SUB]",subject_id)]
        custom_variables["load"] = [("[SUB_TOTALTIME_SUB]",time)]
        # Fill in templates with the experiments
        template_experiments(battery_dest=battery_dest,
                             battery_repo=base["battery_repo"],
                             valid_experiments=base["experiments"],
                             template_exp=template_exp,
                             template_exp_output=template_exp_output,
                             custom_variables=custom_variables)
        return battery_dest    
    else:
        print("Folder exists at %s, cannot generate." %(battery_dest))


def generate(battery_dest=None,battery_repo=None,experiment_repo=None,experiments=None,config=None,make_config=True,warning=True,time=30):
    '''generate
    will create a battery from a template and list of experiments
    :param battery_dest: is the output folder for your battery. This folder MUST NOT EXIST. If not specified, a temp folder is created
    :param battery_repo: location of psiturk-battery repo to use as a template. If not specified, will be downloaded to a temporary directory
    :param experiment_repo: location of a expfactory-experiments repo to check for valid experiments. If not specified, will be downloaded to a temporary directory
    :param experiments: a list of experiments, meaning the "exp_id" variable in the config.json, to include. This variable also conincides with the experiment folder name.
    :param config: A dictionary with keys that coincide with parameters in the config.txt file for a expfactory experiment. If not provided, a dummy config will be generated.
    :param make_config: A boolean (default True) to control generation of the config. If there is a config generated before calling this function, this should be set to False.
    :param warning: Show config.json warnings when validating experiments. Default is True
    :param time: maximum amount of time for battery to endure (default 30 minutes) to select experiments
    '''
    if battery_dest == None:
        battery_dest = tempfile.mkdtemp()
        shutil.rmtree(battery_dest)

    # We can only generate a battery to a folder that does not exist, to be safe
    if not os.path.exists(battery_dest):

        base = generate_base(battery_dest=battery_dest,
                             tasks=experiments,
                             experiment_repo=experiment_repo,
                             battery_repo=battery_repo,
                             warning=warning,
                             add_surveys=False)

        custom_variables = dict()
        custom_variables["load"] = [("[SUB_TOTALTIME_SUB]",time)]

        # Fill in templates with the experiments
        template_experiments(battery_dest=battery_dest,
                             battery_repo=base["battery_repo"],
                             valid_experiments=base["experiments"],
                             custom_variables=custom_variables)

        # Generte config
        if make_config:
            if config == None:
                config = dict()
            generate_config(battery_dest,config)

        return battery_dest
    else:
        print("Folder exists at %s, cannot generate." %(battery_dest))

        
def template_experiments(battery_dest,battery_repo,valid_experiments,template_load=None,template_exp=None,
                         template_exp_output=None,custom_variables=None):
    '''template_experiments:
    For each valid experiment, copies the entire folder into the battery destination directory, and generates templates with appropriate paths to run them
    :param battery_dest: full path to destination folder of battery
    :param battery_repo: full path to psiturk-battery repo template
    :param valid_experiments: a list of full paths to experiment folders to include
    :param template_load: the load_experiments.js template file. If not specified, the file from the battery repo is used.
    :param template_exp: the exp.html template file that runs load_experiment.js. If not specified, the psiturk file from the battery repo is used.
    :param template_exp_output: The output file for template_exp. if not specified, the default psiturk templates/exp.html is used
    :param custom_variables: A dictionary of custom variables to add to templates. Keys should either be "exp" or "load", and values should be tuples with the first index the thing to sub (eg, [SUB_THIS_SUB]) and the second the substitition to make.
    '''
    # Generate run template, make substitutions
    if template_load == None:
        template_load = "%s/static/js/load_experiments.js" %(battery_repo)
    if template_exp == None:
        template_exp = "%s/templates/exp.html" %(battery_repo)
    if template_exp_output == None:
        template_exp_output = "%s/templates/exp.html" %(battery_dest)
    load_template = get_template(template_load)
    exp_template = get_template(template_exp)
    valid_experiments = move_experiments(valid_experiments,battery_dest)
    loadstatic = get_load_static(valid_experiments) 
    concatjs = get_concat_js(valid_experiments) 
    timingjs = get_timing_js(valid_experiments)
    load_template = sub_template(load_template,"[SUB_EXPERIMENTCONCAT_SUB]",concatjs)
    exp_template = sub_template(exp_template,"[SUB_EXPERIMENTSTATIC_SUB]",loadstatic)
    load_template = sub_template(load_template,"[SUB_EXPERIMENTTIMES_SUB]",str(timingjs)) 

    # Add custom user variables
    if custom_variables != None:
        if "exp" in custom_variables:
            exp_template = add_custom_variables(custom_variables["exp"],exp_template)
        if "load" in custom_variables:
            load_template = add_custom_variables(custom_variables["load"],load_template)

    # load experiment scripts
    if not os.path.exists("%s/static/js" %(battery_dest)):
        os.mkdir("%s/static/js" %(battery_dest))
    template_output = "%s/static/js/load_experiments.js" %(battery_dest)
    filey = open(template_output,'w')
    filey.writelines(load_template)
    filey.close()    

    # exp.html template
    filey = open(template_exp_output,'w')
    filey.writelines(exp_template)
    filey.close()    


def add_custom_variables(custom_variables,template):
    '''add_custom_variables takes a list of tuples and a template, where each tuple is a ("[TAG]","substitution") and the template is an open file with the tag.
    :param custom_variables: a list of tuples (see description above)
    :param template: an open file to replace "tag" with "substitute"
    '''
    for custom_var in custom_variables:
        template = sub_template(template,custom_var[0],str(custom_var[1]))
    return template

def move_experiments(valid_experiments,battery_dest,repo_type="experiments"):
    '''move_experiments
    Moves valid experiments into the experiments folder in battery repo
    :param valid_experiments: a list of full paths to valid experiments
    :param battery_dest: full path to battery destination folder
    :param repo_type: the kind of task to move (default is experiments)
    '''

    moved_experiments = []
    for valid_experiment in valid_experiments:
        try:
            experiment_folder = os.path.basename(valid_experiment)
            copy_directory(valid_experiment,"%s/static/%s/%s" %(battery_dest,repo_type,experiment_folder))
            moved_experiments.append(valid_experiment)
        except:
           print("Cannot move %s, will not be added." %(valid_experiment))
    return moved_experiments


def generate_config(battery_dest,fields):
    '''generate_config
    takes a dictionary, and for matching fields, substitues and prints to "config.txt" in a specified battery directory
    :param battery_dest: should be the copied, skeleton battery folder in generation
    :param fields: should be a dictionary with fields that match those in the config non matching fields will be ignored.
    '''
    config = get_config()
    # Convert dictionaries back to string
    for l in range(len(config)):
        line = config[l]
        if isinstance(line,dict):
            linekey = line.keys()[0]
            if linekey in fields.keys():
                config[l][linekey] = fields[linekey]
            config[l] = "%s = %s" %(linekey,config[l][linekey])
    config = "\n".join(config)    
    save_template("%s/config.txt" %battery_dest,config)
    return config



def get_config():
    '''get_config
    load in a dummy config file from expfactory
    '''
    module_path = get_installdir()
    template = "%s/templates/config.txt" %(module_path)
    config = get_template(template)
    config = config.split(os.linesep)
    for l in range(len(config)):
        line = config[l]
        if len(line)>0:
            if line[0]!="[":
                fields = [x.strip(" ") for x in line.split("=")]
                config[l] = {fields[0]:fields[1]} 
    return config


def get_load_static(valid_experiments,url_prefix="",unique=True):
    '''get_load_static
    return the scripts and styles as <link> and <script> to embed in a page directly
    :param unique: return only unique scripts [default=True]
    '''
    loadstring = ""
    for valid_experiment in valid_experiments:
        experiment = load_experiment(valid_experiment)
        css,js = get_stylejs(experiment,url_prefix=url_prefix)
        loadstring = "%s%s%s" %(loadstring,js,css)        
    if unique == True:
        scripts = loadstring.split("\n")
        scripts_index = list(set(scripts, return_index=True))[1]
        # This ensures that scripts are loaded in same order as specified in config.json
        unique_scripts = [scripts[idx] for idx in sorted(scripts_index)]
        loadstring = "\n".join(unique_scripts)
    return loadstring

def get_experiment_run(valid_experiments,deployment="local"):
    '''get_experiment_run
    returns a dictionary of experiment run code (right now just jspsych init objects)
    :param valid_experiments: full path to valid experiments folders, OR a loaded config.json (dict)
    '''
    runs = dict()
    for valid_experiment in valid_experiments:
        if not isinstance(valid_experiment,dict):
            experiment = load_experiment(valid_experiment)[0]
        else:
            experiment = valid_experiment
        tag = str(experiment["exp_id"])
        if experiment["template"] == "jspsych":
            runcode = get_jspsych_init(experiment,deployment=deployment)
        runs[tag] = runcode
    return runs

# Functions below are for psiturk battery
def get_load_js(valid_experiments,url_prefix=""):
    '''get_load_js
    Return javascript to load list of valid experiments, based on psiturk.json
    :param valid_experiments: a list of full paths to valid experiments to include

    ..note::
        Format is:
         {
		case "simple_rt":
			loadjscssfile("static/css/experiments/simple_rt.css","css")
			loadjscssfile("static/js/experiments/simple_rt.js","js")
			break;
		case "choice_rt":
			loadjscssfile("static/css/experiments/choice_rt.css","css")
			loadjscssfile("static/js/experiments/choice_rt.js","js")
			break;

          ...
          }

    '''
    loadstring = "\n"
    for valid_experiment in valid_experiments:
        experiment = load_experiment(valid_experiment)[0]
        tag = str(experiment["exp_id"])
        loadstring = '%scase "%s":\n' %(loadstring,tag)
        for script in experiment["run"]:
            fname,ext = os.path.splitext(script)
            ext = ext.replace(".","").lower()
            # If the file is included in the experiment
            if len(script.split("/")) == 1:                
                loadstring = '%s         loadjscssfile("%sstatic/experiments/%s/%s","%s")\n' %(loadstring,url_prefix,tag,script,ext)
            else:
                loadstring = '%s         loadjscssfile("%s%s","%s")\n' %(loadstring,url_prefix,script,ext)
        loadstring = "%s         break;\n" %(loadstring)
    return loadstring


def get_concat_js(valid_experiments):
    '''get_concat_js
    Return javascript concat section for valid experiments, based on psiturk.json
    :param valid_experiments: full paths to valid experiments to include

    ..note::

			case "simple-rt":
				experiments = experiments.concat(simple-rt_experiment)
				break;
			case "choice-rt":
				experiments = experiments.concat(choice-rt_experiment)
				break;

               Format for experiment variables is [exp_id]_experiment

    '''
    concatjs = "\n"
    for valid_experiment in valid_experiments:
        experiment = load_experiment(valid_experiment)[0]
        tag = str(experiment["exp_id"])
        concatjs = '%scase "%s":\n' %(concatjs,tag)
        concatjs = '%s      experiments = experiments.concat(%s_experiment)\n' %(concatjs,tag)
        concatjs = '%s      break;\n' %(concatjs)
    return concatjs

def get_timing_js(valid_experiments):
    '''get_timing_js
    Produce string (json / dictionary) of experiment timings
    :param valid_experiments: a list of full paths to valid experiments to include

    ..note::

         Produces the following format for each experiment

         {name:"simple_rt", time: 3.5}, {name:"choice_rt", time: 4}, ...
    
    
    '''
    timingjs = []
    for valid_experiment in valid_experiments:
        experiment = load_experiment(valid_experiment)[0]
        timingjs.append({"name":str(experiment["exp_id"]),"time":experiment["time"]})
    return timingjs
