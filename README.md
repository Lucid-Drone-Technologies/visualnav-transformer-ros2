# General Navigation Models: GNM, ViNT and NoMaD

This repository is a port of [visualnav-transformer](https://github.com/robodhruv/visualnav-transformer) to ROS2. Its purpose is to make running the models more straightforward by providing a Dockerfile with all dependencies set up. For more details on the models, please refer to the original repository.

### Open Isaac Sim

1. Activate conda environment
```bash
conda activate env_isaacsim
```

2. Open Isaac Sim. Takes 1-2 min. Ignore the Isaac Sim not responding window
```bash
isaacsim omni.isaac.sim
```

3. Open the Carter Navigation Simulation
```bash
Isaac Examples -> ROS2 -> Navigation -> Carter Navigation
```

### Running the code

1. Clone the repository:
```bash

git clone https://github.com/RobotecAI/visualnav-transformer-ros2
cd visualnav-transformer-ros2
mkdir model_weights && cd model_weights
pip3 install gdown 
gdown https://drive.google.com/uc?id=1YJhkkMJAYOiKNyCaelbS_alpUpAJsOUb -O nomad.pth
```

2. Build the Docker image:
```bash
docker build -t visualnav_transformer:latest .
```

3. Run the Docker container(Please replace the "/home/visualnav-transformer-ros2" with your folder path):
```bash
docker run -it --rm --gpus=all --name gnm -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY --network=host --user root -v /home/ubuntu/visualnav-transformer-ros2:/visualnav-transformer visualnav_transformer:latest
```

Open same docker container in different terminal
```bash
docker exec -i -t gnm /bin/bash
```

4. Run the model:

Inside the container, run the following commands:
```bash
poetry shell
python src/visualnav_transformer/deployment/src/explore.py
```
This will run the model and publish the predicted waypoints to a ROS2 topic, but your robot will not move yet. Next to running the model you have to run a script that will publish the movement commands to the robot.

```bash
python scripts/publish_cmd.py
```

Now the robot should start moving based on the model's predictions.

To visualize the waypoints that the model is outputting you can run the following command:
```bash
python scripts/visualize.py
```
This code will publish the output image in a topic called "visualize_output"

You can open rivz2 to visualize it. 

### Creating a topomap of the environment

In order to navigate to a desired goal location, the robot needs to have a map of the environment. To create a topomap of the environment, you can run the following command:
```bash
python src/visualnav_transformer/deployment/src/create_topomap.py
```
The script will save an image from the camera every second (this interval can be changed with the `-t` parameter). Now you can drive the robot around the environment manually (using your navigation stack or teleop) and the map will be saved automatically. After you have driven around the environment, you can stop the script and proceed to the next step.

### Navigation
Having created a topomap of the environment, you can now run the navigation script:
```bash
python src/visualnav_transformer/deployment/src/navigate.py
```
By default the robot will try to follow the topomap to reach the last image captured. You can specify a different goal image by providing an index of an image in the topomap using the `--goal-node` parameter.
