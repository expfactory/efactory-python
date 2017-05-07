#!/usr/bin/env python

'''
script.py: part of expfactory api
Runtime executable

Copyright (c) 2016-2017 Vanessa Sochat, Stanford University

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from expfactory.views import (
    preview_experiment, 
    run_battery, 
    run_single
)

from expfactory.battery import (
    generate, 
    generate_local
)

from expfactory.experiment import (
    validate, 
    load_experiment
)

from expfactory.tests import validate_surveys

from glob import glob
import argparse
import sys
import os



def get_parser():

    parser = argparse.ArgumentParser(
    description="generate experiments and infrastructure to serve them.")

    parser.add_argument("--folder", dest='folder', help="full path to single experiment folder (for single experiment run with --run) or folder with many experiments (for battery run with --run)", type=str, default=None)
    parser.add_argument("--subid", dest='subid', help="subject id to embed in experiments data in the case of a battery run with --run", type=str, default=None)
    parser.add_argument("--experiments", dest='experiments', help="comma separated list of experiments for a local battery", type=str, default=None)
    parser.add_argument("--port", dest='port', help="port to preview experiment", type=int, default=None)
    parser.add_argument("--battery", dest='battery_folder', help="full path to local battery folder to use as template", type=str, default=None)
    parser.add_argument("--time", dest='time', help="maximum number of minutes for battery to endure, to select experiments", type=int, default=99999)
    parser.add_argument('--preview', help="preview an experiment locally (development function)", dest='preview', default=False, action='store_true')
    parser.add_argument('--run', help="run a single experiment/survey or battery locally", dest='run', default=False, action='store_true')
    parser.add_argument("--survey", dest='survey', help="survey to run for a local assessment", type=str, default=None)
    parser.add_argument("--game", dest='game', help="game to run for a local assessment", type=str, default=None)
    parser.add_argument('--validate', dest='validate', help="validate an experiment folder", default=False, action='store_true')
    parser.add_argument('--psiturk', dest='psiturk', help="to be used with the --generate command, to generate a psiturk battery instead of local folder deployment", default=False, action='store_true')
    parser.add_argument('--generate', dest='generate', help="generate (and don't run) a battery with --experiments to a --folder", default=False, action='store_true')
    parser.add_argument("--output", dest='output', help="output folder for --generate command, if a temporary directory is not desired. Must not exist.", type=str, default=None)
    parser.add_argument('--test', dest='test', help="test an experiment folder with the experiment robot", default=False, action='store_true')

    return parser


def main():

    from logman import bot
    parser = get_parser()

    try:
        args = parser.parse_args()
    except:
        parser.print_help()
        sys.exit(0)

    
    # Check if the person wants to preview experiment or battery
    if args.preview == True:
        preview_experiment(folder=args.folder,
                           battery_folder=args.battery_folder,
                           port=args.port)

    # Generate a local battery folder (static)
    elif args.generate == True:

        if args.experiments is not None:

            # Deploy a psiturk battery folder
            experiments = args.experiments.split(",")

            if args.psiturk == True:
                outdir = generate(battery_dest=args.output,
                                  battery_repo=args.battery_folder,
                                  experiment_repo=args.folder,
                                  experiments=experiments,
                                  make_config=True,
                                  warning=False)

            # Deploy a regular battery folder
            else:
                outdir = generate_local(battery_dest=args.output,
                                        subject_id="expfactory_battery_result",
                                        battery_repo=args.battery_folder,
                                        experiment_repo=args.folder,
                                        experiments=experiments,
                                        warning=False,
                                        time=args.time)

            bot.info("Battery generation complete: static files are in %s" %(outdir))

        else:
            bot.info("Please specify list of comma separated experiments with --experiments")

    # Run a local battery
    elif args.run == True:

        # Warn the user about using repos for experiments and battery
        if args.battery_folder == None:
            bot.info("No battery folder specified. Will pull latest battery from expfactory-battery repo")

        if args.folder == None:
            bot.info("No experiments, games, or surveys folder specified. Will pull latest from expfactory-experiments repo")

        if args.survey is not None:
            survey = args.survey.split(",")
            if len(survey) > 0:
                bot.warning("Currently only support running one survey, will run first in list.")
                survey = survey[0]
            run_single(exp_id=survey,
                       repo_type="surveys",
                       source_repo=args.folder,
                       battery_repo=args.battery_folder,
                       port=args.port,
                       subject_id=args.subid)

        if args.game is not None:
            game = args.game.split(",")
            if len(game) > 0:
                bot.warning("Currently only support running one game, will run first in list.")
                game = game[0]
            run_single(exp_id=game,
                       repo_type="games",
                       source_repo=args.folder,
                       battery_repo=args.battery_folder,
                       port=args.port,
                       subject_id=args.subid)

        if args.experiments is not None:
            experiments = args.experiments.split(",")
            run_battery(experiments=experiments,
                        experiment_folder=args.folder,
                        subject_id=args.subid,
                        battery_folder=args.battery_folder,
                        port=args.port,
                        time=args.time)
        else:
            bot.info("Please specify list of comma separated experiments with --experiments")

    # Validate a config.json
    elif args.validate == True:
        if args.folder == None:
            folder = os.getcwd()
        validate(experiment_folder=folder)
        # If a survey, and if validates, also validate survey.tsv
        experiment = load_experiment(folder)[0]
        if experiment["template"] == "survey":
            bot.debug("Validating survey.tsv...")
            survey_repo = os.path.dirname(folder)
            validate_surveys(experiment["exp_id"],survey_repo)

        
    # Run the experiment robot
    elif args.test == True:
        from expfactory.tests import test_experiment
        test_experiment(folder=args.folder,
                        battery_folder=args.battery_folder,
                        port=args.port)

    # Otherwise, just open the expfactory interface
    else:        
        from expfactory.interface import start
        start(port=args.port)    

if __name__ == '__main__':
    main()
