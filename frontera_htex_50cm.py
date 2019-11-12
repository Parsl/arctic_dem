from parsl.config import Config

from parsl.channels import LocalChannel
from parsl.providers import SlurmProvider
from parsl.executors import HighThroughputExecutor
from parsl.launchers import SrunLauncher
from parsl.addresses import address_by_hostname
 
# 1) Initially, if a single node came down, the job that contained that node would fail.  
#   The Swift folks wrote us a workaround where we modified the aprun wrapper to use the -C option 
#   allow the job to continue without that node.
# 2) Next, during the BW warm swaps, their interconnect fabric would go down for up to 2 minutes.  
#    This caused the swift process to miss the "heartbeat" checks with the nodes it was coordinating.  
#    The lack of communication made swift think the nodes were down and so it considered those nodes 
#    dead and did not use them again for the length of the job.  This meant that were being changed
#    for the full node count and only using a handful.
# 3) Due to a security sweep on the login nodes that would shut down our swift processes, we had to 
#    run on the MOM nodes.
# > I've run long running tests (8h) on login nodes without issues so far. I've mailed the stampede 
# > Admins asking for best practice on this.
        
# 4) Our tasks can last a highly variable amount of time, so our max wall time is 48 hours.  But, most 
#    tasks finish in 11 hours.  Swift would not start a new task after the first had finished because 
#    it thought it would not have enough time to accomplish a 48 hour run in the remaining job walltime.
# > Parsl for better-or-worse doesn't take walltimes for individuals apps. So tasks will not differentiate
# > between jobs/nodes. Assuming the apps have mechanisms to restart from internal checkpoints this works
# > out very well.

config = Config(
    retries = 3, # Parsl will retry failed apps upto 3 times before giving up.
    executors=[
        HighThroughputExecutor(
            label="frontera_htex_50cm",
            # Suppress interchange failure on recieving spurious message
            suppress_failure=True,
            # If you turn on Debug logging expect about 1G of logs per hour
            # worker_debug=True,
            address=address_by_hostname(),
            max_workers=1, # Set the maximum # of workers per manager/node.

            # Set the heartbeat params to avoid faults from periods of network unavailability
            # Addresses concern 2)
            heartbeat_period=60,
            heartbeat_threshold=300,

            provider=SlurmProvider(
                cmd_timeout=60,
                channel=LocalChannel(),
                nodes_per_block=100,
                init_blocks=1,
                min_blocks=1,
                max_blocks=25,
                partition='normal',  # Replace with partition name
                scheduler_options='#SBATCH -A FTA-Morin',   # Enter scheduler_options if needed
                worker_init='source /scratch1/06187/cporter/setup_parsl_env.sh',

                # Ideally we set the walltime to the longest supported walltime.
                walltime='48:00:00',

                # Adding --no-kill to ensure that a single node failure doesn't terminate the whole srun job 
                # Addresses concern 1)
                launcher=SrunLauncher(overrides='--no-kill '),

            ),
        )
    ],
)
