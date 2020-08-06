Getting Started
===============

You are probably a researcher that wants to collect behavioral data, and you have very specific requirements for your desired experiments, along with the environment that you will be collecting them in. The Experiment Factory is an open source, modular infrastructure that will make this easy for you. We store all of these components in a version control system called Github including `1) experiments <https://github.com/expfactory/expfactory-experiments>`_, `2) surveys <https://github.com/expfactory/expfactory-surveys>`_, `3) games <https://github.com/expfactory/expfactory-games>`_, and different options for deployment (discussed below). Note that this is now a legacy version of the Experiment Factory. If you are looking for the newer (container-based and reproducible) experiment factory, please see `expfactory/expfactory <https://expfactory.github.io>`_. Before we get started, let's define a few terms.

 - **experiments**: an experiment is a web-based task, survey, or game. This means that it is presented in a browser, and coded in JavaScript, HTML, and CSS. If you look in any of the repos linked above, you will see an experiment is just a folder of files that will render in a browser and present visual and auditory stimuli, as well as collect behavioral metrics like response and reaction time, and accuracy.
 - **battery**: a battery is a bunch of experiments presented in sequence. Typically, in research studies participants are presented with a battery of experiments.
 - **deployment**: refers to where and how you want your participants to take the battery. You may choose to have them come into your lab, and sit at one of your computers. You may went to send your participants a unique, personal link to complete on their own computer. You may also want to serve the experiments from your own private server or database, or from a computer without an internet connection. For all of these situations, the experiment factory offers a solution.

How should you get started? We first recommend that you `try out our paradigms <https://expfactory.github.io/v1/table.html>`_. Your search may stop with this link - you can use this preview table to deploy the current version of an experiment, and data will be downloaded to your browser at the completion of each. If you like what you see, we encourage you to express interest in `expfactory.org <https://expfactory.org/signup>`_, a live deployment of `expfactory docker <https://github.com/expfactory/expfactory-docker>`_ that we are using at Stanford to deploy experiments locally and to Amazon Mechanical Turk. We are considering opening up this site to the public to offer Experiments as a Service (EaS) depending on (your!) expressed user interest. In the meantime, if you are comfortable with command line tools like git and pip, you can jump right into our `development docs <https://expfactory.readthedocs.org/en/latest/development.html>`_ or `deployment docs <https://expfactory.readthedocs.org/en/latest/deployment.html>`_. We provide many avenues for deploying experiments, and all of this software is open source and free for you to use. We have a vision for reproducible, collaborative science, and want you to have control over your experiments and choice for deployment. Thus, we provide details about deployment options in the following sections.


I want to generate a custom battery
-----------------------------------

First you should follow instructions for `installation <https://expfactory.readthedocs.org/en/latest/installation.html>`_. The Experiment Factory provides several options for deploying a battery, running one or more experiments locally, or generating a static battery to run on your own web server. A battery of experiments is a selection of experimental paradigms that are presented in sequence. We have made it easy to select one or more experiments from any of our repos, plug them into a `expfactory battery <https://www.github.com/expfactory/expfactory-battery>`_, and deploy.  What are your deployment options? You can use the paradigms as single units, as is, `at expfactory.github.io <https://expfactory.github.io/v1/table.html>`_, run a battery on demand using the command line tool, generate a custom folder to run later, or deploy a more substantial infrastructure, including `vagrant virtual machines <https://github.com/expfactory/expfactory-vm>`_, a `docker-based infrastructure <https://www.github.com/expfactory/expfactory-docker>`_.


Local Deployment of Experiments
'''''''''''''''''''''''''''''''
A local deployment means running one or more experiments on a local machine, such as your computer or a lab machine. The simplest thing you can do is install the expfactory tool, and then run a battery of experiments:

::

      expfactory --run --experiments stroop,nback


This command will use the latest experiments in the repo. If you want to ensure that your experiments do not change, or if you will be running the experiments without an internet connection, or if you want to modify experiments for your need, we recommend cloning the experiments repo, and specifying it as an argument to the command:

::

      git clone https://github.com/expfactory/expfactory-experiments
      expfactory --run --experiments stroop,nback --folder expfactory-experiments


You can do the same for a battery folder:

::

      git clone https://github.com/expfactory/expfactory-experiments
      expfactory --run --experiments stroop,nback --battery expfactory-battery


For each of the above, this will open up your browser to run the experiments, and data is stored to your computer via a file downloaded in the browser. You might want to specify a participant id to customize the naming of the output data, and to embed the id in the data itself:


::

      git clone https://github.com/expfactory/expfactory-experiments
      expfactory --run --experiments stroop,nback --subid DNS001


The above can also be done for any of our surveys or small selection of games:


::

     expfactory --run --survey bis11_survey
     expfactory --run --game bridge_game



Generation of Local Battery
'''''''''''''''''''''''''''
If you want to generate a custom folder and run it later, you can use the expfactory command line "--generate" command. This situation is ideal for generating your own static HTML/CSS files to put on your own web server. We recommend our Windows users to do this in some Linux environment (if your university has a shared cluster or on a Virtual Machine) and then to move the battery folder back onto the Windows Machine. To generate a battery folder:

::

      expfactory --generate --experiments stroop,nback


Or to generate a Psiturk battery folder:

::

      expfactory --generate --experiments stroop,nback --psiturk


If you don't specify an output folder, a temporary directory will be created. For each of the above, you can specify the --output command, a full path to a folder (that does not exist) that you want the battery generated in. 



Expfactory Portal
.................
If you are a Linux or Unix-based user and want to dynamically generate a custom battery for Psiturk (called a "folder" deployment), or a Virtual Machine with Vagrant, you can do so with the command line tool: 

:: 

      expfactory


Which will open up a view in your browser. You can then click "battery." The web interface will take you through the following steps:

* A. collection of experiment details
* B. database connection parameters
* C. selection of local (folder) experiment, or deployment to AWS.
* D. selection of experiments

More `details are provided <https://expfactory.readthedocs.org/en/latest/deployment.html>`_ about choosing a deployment, and configuring your battery.


Expfactory-docker
.................
The Experiment Factory docker is a set of containers that can be run locally, or again on the cloud. The entire application comes packaged in a set of Docker images, meaning that installation and deployment of experiments happens in a web interface deployed by Docker Compose. We plan to offer experiment deployment as a service at `expfactory.org <https://www.expfactory.org>`_ and encourage you to `sign up <https://www.expfactory.org/signup>`_ to express interest. You can also `deploy our Docker infrastructure <https://www.expfactory.org/signup>`_ on your own server, however experience with docker and cloud computing is required.


I want to preview available experiments
---------------------------------------

We provide static versions of all experiments, along with meta-data, in our `expfactory-experiments <https://expfactory.github.io/v1>`_ github pages. You can preview the currently available experiments in our `online portal <https://expfactory.github.io/v1/table.html>`_. You can generate this portal on the fly on your local machine as well:

::

      from expfactory.views import generate_experiment_web
      output_folder = os.path.abspath("/home/vanessa/Desktop/web")
      generate_experiment_web(output_folder)


The output folder does not need to exist. This will generate the equivalent interface hosted on expfactory.github.io.


I want to contribute an experiment
----------------------------------

The short story is that all of the experiments that can be selected are just folders on Github, https://github.com/expfactory/expfactory-experiments, and you can contribute by modifying an existing experiment or creating a new one by submitting a PR to this repository. Adding surveys are even easier, as a survey is just a tab delimited file in a folder in the expfactory-surveys repo. For complete details about experiment, survey, and game contributions, please see our `development <https://expfactory.readthedocs.org/en/latest/development.html?highlight=contributing#contributing-to-experiments>`_ pages. 


I want to learn about the expfactory-python functions
-----------------------------------------------------

The generation of the batteries, along with experiment validation, and virtual machine deployment, are controlled by the expfactory-python functions. You can see complete function documentation under :ref:`modindex`, and we welcome any contributions to the code base via Github pull requests (PRs) or `isses <https://www.github.com/expfactory/expfactory-python/issues>`_. We provide a few examples below of running tests and generating visualizations.

Run the experiment testing robot
''''''''''''''''''''''''''''''''

::

      expfactory --test


Validate an experiment folder
'''''''''''''''''''''''''''''

::

      expfactory --validate


Preview a single experiment
'''''''''''''''''''''''''''

::

      expfactory --preview


Generate the entire expfactory.github.io interface
''''''''''''''''''''''''''''''''''''''''''''''''''

::
      
      from expfactory.views import generate_experiment_web
      web_folder = '/home/vanessa/Desktop/site'
      generate_experiment_web(web_folder) 


You can then run an experiment robot over experiments in this folder, either for all experiments:

::

      experiment_robot_web(web_folder)


or a subset of experiments

::

      experiment_robot_web(web_folder,experiment_tags=changed_experiments)


Checking static javascript with jshint
''''''''''''''''''''''''''''''''''''''
We recommend using the docker image to do this, across many experiment directories at once:

::

      docker pull hyzual/jshint
      cd expfactory-experiments
      sudo docker run -it -v $(pwd):/lint hyzual/jshint --config /lint/.jshint_config .


Validate an entire set of experiment directories
''''''''''''''''''''''''''''''''''''''''''''''''

::

    from expfactory.tests import validate_experiment_directories, validate_experiment_tag
    validate_experiment_directories('expfactory-experiments')
    validate_experiment_tag('expfactory-experiments')


