ArcticDEM with Parsl
====================

This is a preliminary attempt at converting existing swift workflows designed for Bluewaters over
to Parsl with Stampede2 as the execution target


Setting up Stampede2
--------------------

Load the Python module on Stampede

>>> module load python3/3.6.3

Create python environment

>>> python3 -m venv parsl_0.7.2_py3.6.3

Activate the env

>>> source parsl_0.7.2_py3.6.3/bin/activate

Install parsl

>>> pip install parsl==0.7.2

Create a setup script with the following

>>> echo "module load python3/3.6.3" >> setup_parsl_env.sh 
>>> echo "source ~/parsl_0.7.2_py3.6.3/bin/activate" >> setup_parsl_env.sh


Update the Parsl config for user specific
-----------------------------------------

The configuration used for tests is the `stampede2_htex.py` config. The following bits
need to be updated with user and workflow specifics.

1. `max_workers` : Update this with the max # of tasks that could execute together on a single node
2. `partition` : Preferred partition
3. `scheduler_options` : Update the string with the right account information
4. `worker_init`: Make sure that the setup script path is correct
5. `walltime` : Update to match app durations


Running the workflow
--------------------

Activate the environment

>>> source ~/setup_parsl_env.sh

Update the configs

>>> emacs arctic_dem/stampede2_htex.py

Run!

>>> python3 parsl_runner.py -s /scratch/06187/cporter/results/region_03_conus/jobfiles/32m -f stampede2_htex

Reference
---------

As for gotchas that we had to work through with BW, here is a brief list.  Let me know if you want more details:

1) Initially, if a single node came down, the job that contained that node would fail.  The Swift folks wrote us a workaround where we modified the aprun wrapper to use the -C option allow the job to continue without that node.
2) Next, during the BW warm swaps, their interconnect fabric would go down for up to 2 minutes.  This caused the swift process to miss the "heartbeat" checks with the nodes it was coordinating.  The lack of communication made swift think the nodes were down and so it considered those nodes dead and did not use them again for the length of the job.  This meant that were being changed for the full node count and only using a handful.
3) Due to a security sweep on the login nodes that would shut down our swift processes, we had to run on the MOM nodes.
4) Our tasks can last a highly variable amount of time, so our max wall time is 48 hours.  But, most tasks finish in 11 hours.  Swift would not start a new task after the first had finished because it thought it would not have enough time to accomplish a 48 hour run in the remaining job walltime.

I assume most of these would still be an issue using Swift on any TACC system, so we would be happy to swift to Parsl if these problems are addressed.

python3 parsl_runner.py -s test_samples/region_03_conus/jobfiles/2m -f stampede2_htex
