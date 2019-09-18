#!/usr/bin/env python3

import argparse
import time
import os
import glob
import parsl
from parsl.app.app import python_app, bash_app
from parsl import File


@bash_app(cache=True)
def exec_script(scriptpath, stdout=None, stderr=None, mock=False):
    """ This function must return a command line executable as a string.

    Parameters
    ----------
        scriptpath: str
            Path to the script to be executed
        stdout: str
            Path to file to which stdout is to be piped
        stderr: str
            Path to file to which stderr is to be piped
        mock: Bool
            When called with mock=True, the command to be executed will be echoed
            to the stdout file.
    """
    if mock:
        return f'''echo "/bin/bash {scriptpath}" '''

    else:
        return f"/bin/bash {scriptpath}"


def find_and_launch(source):
    """
    Parameters
    ----------

    source: str
         Directory path to the source dir.

    """
    if not os.path.isdir(source):
        raise Exception("Source dir:{} is not a directory".format(source))

    script_fus = []
    for script_file in glob.glob(source + "/qsub*sh"):
        scriptpath = os.path.abspath(script_file)
        # Test if task is already completed
        outfile = os.path.basename(scriptpath)[5:-3]
        resdir = os.path.basename(os.path.dirname(scriptpath))
        stripdir = "{}_{}".format(outfile[:47],resdir)
        outpath = os.path.join(os.path.dirname(scriptpath.replace("jobfiles","tif_results")),stripdir,outfile)
        if not(os.path.isfile(outpath+"_dem_smooth.tif") and os.path.isfile(outpath+"_matchtag.tif") \
                and os.path.isfile(outpath+"_ortho.tif") and os.path.isfile(outpath+"_meta.txt") \
                and not os.path.isdir(outpath)): 

	        print("Scriptpath : {}".format(scriptpath))
        	fu = exec_script(File(scriptpath),
        	                 stdout=scriptpath + '.stdout',
                	         stderr=scriptpath + '.stderr')
	        script_fus.append(fu)

    print("{} unfinished tasks".format(len(script_fus)))

    # Wait for all the scripts to exit
    [sf.result() for sf in script_fus]
    print("All tasks complete")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", required=True,
                        help="Directory path with scripts to launch")
    parser.add_argument("-d", "--debug", action='store_true',
                        help="Debug flag, when provided will dump debug logging to stdout")
    parser.add_argument("-f", "--fileconfig", required=True,
                        help="Parsl config to use for this run specified without the .py extension")

    args = parser.parse_args()

    if args.debug:
        parsl.set_stream_logger()

    config = None
    exec("from {} import config".format(args.fileconfig))
    parsl.load(config)

    x = find_and_launch(args.source)


