## 0. Introduction
This repository contains the  modified source code for the SIGCOMM'21 paper "Network Planning with Deep Reinforcement Learning".
The code base was modeified to support TF 2.0 and pytorch 1.13 with cu117 toolkit.

### Notes
The network topologies and the trained models used in the paper are not open-sourced. One can create synthetic topologies according to the problem formulation in the paper or modify the code for their own use case.

For COS561: We provide our example topologies in the /source/data/topologies folder. All topologies come from the Internet Topology Zoo.

## 1. Environment config updated to work on the cluster

### Step 0: download the git repo
```
git clone https://github.com/iarmourgarb/neuroplan.git
```
### Step 1: Make conda environment
```
conda create --name <env> python=3.7
conda activate <env>
conda install -c conda-forge mpi4py
pip install protobuf==3.20.*
pip install openpyxl
```

Then you need to set your environment variables by changing the gurobi.sh file


### Step 2: Install gurobi and mpi4py in conda env
```
wget https://packages.gurobi.com/9.0/gurobi9.0.2_linux64.tar.gz
tar xvfz gurobi9.0.2_linux64.tar.gz
cd gurobi902/linux64/src/build/
make
cp libgurobi_c++.a ../../lib/
```

Make sure your Gurobi solver works: `gurobi_cl /opt/gurobi902/linux64/examples/data/coins.lp`

Academic license:
- Install the license here: https://www.gurobi.com/downloads/free-academic-license/



### Step 3: install python dependencies in the conda env
```
cd <repo>/spinningup
pip install -e .
pip install tensorflow
conda install pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 pytorch-cuda=12.1 -c pytorch -c nvidia
pip install networkx pulp pybind11 xlrd==1.2.0
```
### Step 4: compile C++ program with pybind11
```
cd <repo>/source/c_solver
./compile.sh
```
## 2. Content
- source
    - c_solver: C++ implementation with Gurobi APIs for ILP solver and network plan evaluator
    - planning: `ILP` and `ILP-heur` implementation
    - results: store the provided trained models and solutions, and the training log
    - rl: the implementations of Critic-Actor, RL environment and RL solver 
    - simulate: python classes of flow, spof, and traffic matrix
    - topology: python classes of network topology (both optical layer and IP layer)
    - `test.py`: the main script used to reproduce results
- spinningup
    - adapted from [OpenAI Spinning Up](https://github.com/openai/spinningup)
- `gurobi.sh`
    - used to install Gurobi solver
## 3. Reproduce results (for SIGCOMM'21 artifact evaluation)
### Notes 
- Some data points are time-consuming to get (i.e., First-stage for A-0, A-0.25, A-0.5, A-0.75 in Figure 8 and B, C, D, E in Figure 9).
- We recommend distributing different data points and differetnt experiments on multiple AWS instances to run simultaneously.
- The default `epoch_num` for Figure 10, 11 and 12 is set to be 1024, to guarantee the convergence. The training process can be terminated manually if convergence is observed.
### How to reproduce
- `cd <repo>/source`
- Figure 7: `python test.py fig_7 <epoch_num> <topology>` , `epoch_num` can be set smaller than 10 (e.g. 2) to get results faster topologies are in [A,B,C,D,E].


## 4. Contact
Original NeuroPlan contact: For any question, please contact `hzhu at jhu dot edu`.
