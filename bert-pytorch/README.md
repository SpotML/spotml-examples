In this tutorial, we will show you how to fine-tune BERT on the IMDB dataset. The task is to classify whether movie reviews are positive or negative.

We will run train using Pytorch on an aws instance using SpotML.

## Steps:
Tutorial time - 5 minutes

#### 0. AWS Setup (one time)

Make sure you've done the one time AWS setup [here](https://docs.spotml.io/aws-setup)

----------

#### 1. Clone the repo
```
git clone https://github.com/SpotML/spotml-examples.git 
cd spotml-examples/bert-pytorch
```

#### 2. Start the instance
```
spotml start
```
Wait for the instance to start. This will spawn an instance in your aws account. You should see an output like below

```

Tracking instance uptime now.


+--------------------+---------------------+
| Instance State     | running             |
+--------------------+---------------------+
| Instance Type      | g4dn.xlarge         |
+--------------------+---------------------+
| Availability Zone  | us-east-1a          |
+--------------------+---------------------+
| Public IP Address  | 54.221.156.106      |
+--------------------+---------------------+
| Purchasing Option  | On-Demand Instance  |
+--------------------+---------------------+
| Instance Price     | $0.5260 (us-east-1) |
+--------------------+---------------------+
| Tracking Idle Time | True                |
+--------------------+---------------------+

Use the "spotml sh" command to connect to the container.
```

By default, SpotML will track the instance for idle time. If the instance is idle for more than 30 mins, it's automatically terminated.
#### 3. SSH into instance
```
spotml sh
```
SpotML uses [tmux](https://github.com/tmux/tmux/wiki) sessions.
So to exit the ssh session type `Ctrl + b`, then type `d` to disconnect from the session.


#### 4. Run train.
Once you have ssh'ed into the session run  
```
python train.py
```

You should see an output like this 
```angular2html
***** Running training *****
  Num examples = 1000
  Num Epochs = 1
  Instantaneous batch size per device = 8
  Total train batch size (w. parallel, distributed & accumulation) = 8
  Gradient Accumulation steps = 1
  Total optimization steps = 125
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████| 125/125 [01:36<00:00,  1.27it/s]

Training completed. Do not forget to share your model on huggingface.co/models =)


{'train_runtime': 96.9102, 'train_samples_per_second': 10.319, 'train_steps_per_second': 1.29, 'train_loss': 0.5495736083984375, 'epoch': 1.0}        
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████| 125/125 [01:36<00:00,  1.29it/s]
The following columns in the evaluation set  don't have a corresponding argument in `BertForSequenceClassification.forward` and have been ignored: text.
***** Running Evaluation *****
  Num examples = 1000
  Batch size = 8
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████| 125/125 [00:36<00:00,  3.46it/s]
```
That's it, you have trained a BERT model inside an aws instance.


## Spot instance Managed run (optional):

If you are training 
1. A long-running model that could last for hours/days.
2. Want to use a spot instance to save cost

Then you will want to resume from spot interruptions and continue training from last checkpoint. To do that follow below steps:

#### 1. Update config file to use spot instance
Open the spotml.yaml file and find the line that says `spotStrategy`. 
Change it to 
```yaml
spotStrategy: spot
```

#### 2. Turn off the on-demand instance
```
spotml stop
```
We will turn off the on-demand instance that was launched so that we can start a new spot instance.

#### 3. Run the script
```
spotml run train
```
SpotML tries to spawn a new spot instance and runs the below script in the instance from `spotml.yaml`
```yaml
scripts:
  train: |
    python train.py
```

Note that if a spot instance is not available, spotML backend service keeps 
trying every 15 mins, until it can spawn the instance.
So you can turn off your laptop and do other things, while SpotML tries to 
schedule the run. 

Secondly if a spot instance is interrupted, SpotML automatically puts the run back in queue to spawn another 
instance until the run completes. We've configured our train.py to 
automatically resume from latest checkpoint
```python
if any(File.endswith(".pt") for File in os.listdir(checkpoint_directory)):
    trainer.train(resume_from_checkpoint=True)
else:
    trainer.train()
```

#### 4. Check Status
```
spotml status
```
You can check the status of the `instance`, and the `run` with the above command.

To also check any logs generated when starting the instance type  
```angular2html
spotml status --logs
```

#### 4. SSH into the instance to see run logs

Once you see the run status as `RUNNING` from the `status` command you can ssh into the actual run session by typing
```angular2html
spotml sh run
```
This opens the tmux session where spotML ran the `train` command.
To exit the ssh session type `Ctrl + b`, then type `d` to disconnect from the session.
#### 5. To stop the run

If you intend to cancel the scheduled run, type 
```
spotml run stop
```