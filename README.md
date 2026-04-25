# Mouse Genome Machine Learning Data Pipeline 

This repository contains the infrastructure and configuration code for a mouse genome machine learning data pipeline. It uses **Terraform** to provision infrastructure and **Ansible** to configure the host and worker nodes.

---

## Prerequisites

Ensure the following are installed on your **local machine**:

- Terraform
- An SSH key pair

## Infrastructure Setup (Terraform)

1. Configure instance labels and variables in Terraform as required.

2. Provision the infrastructure:
   ```bash
   terraform apply
   ```

3. Copy your SSH key to the host machine:
    ```bash
    scp -i ~/.ssh/<KEY_NAME> ~/.ssh/<KEY_NAME> almalinux@<HOST_IP>:/home/almalinux/.ssh/
    ```

## Host Machine Setup
Install required tools and clone the repository onto your host node:

```bash
sudo dnf install -y git
sudo dnf install -y ansible
git clone https://gitlab2.ds4eng.condenser.arc.ucl.ac.uk/ucabmjc/comp0239.git comp0239_cw
```
*NOTE: You may require a username and a Personal Access Token (PAT) to access the remote Git repository.*

## Network Configuration (Inventory Setup)
Before running Ansible, you must transfer the inventory configuration from your local machine to the host node.

1. On your local machine, view the contents of the generated hosts file:

```bash
cat ../ansible/hosts
```

2. Copy the entire output to your clipboard.
3. SSH into the host machine.
4. Open the hosts file on the host node and paste the copied output:

```bash
vim ~/comp0239_cw/ansible/hosts
```
*(Save and exit the file).*

## Configuration (Ansible)
Once the hosts file is securely on the host node, you can configure the cluster.

1. On the host machine, navigate to the Ansible directory:

```bash
cd ~/comp0239_cw/ansible/
```
2. Run the Ansible playbook:

```bash
ansible-playbook -i hosts full.yaml --key-file ~/.ssh/<KEY_NAME>
```
This will automatically configure BeeGFS, install Slurm, set up Prometheus metrics, and prepare the Python virtual environments across the host and all worker nodes.

Running the Data Pipeline
Once the infrastructure has been configured with Ansible, the data pipeline can be executed from the host machine using the Slurm workload manager.

## Running the Standard Analysis:

1. SSH into the host machine.

2. Navigate to the source code directory:

```bash
cd ~/comp0239_cw/src/
```
3. Launch the distributed pipeline:

```bash
./launch_job.sh
```
This script dynamically chunks the dataset and distributes the Hugging Face inference jobs across the worker nodes in parallel.

### Running the Capacity Test:

To verify cluster stability, a capacity test is available which runs the system at maximum capacity for over 24 hours. This is achieved by chaining 5 iterations of the full dataset analysis together.

1. From the src directory, launch the capacity test:

```bash
./capacity_test.sh
```
You can monitor the queued and running jobs in real-time by typing:

```bash
squeue
```

## Viewing and Monitoring Results

**Viewing Pipeline Results:**
Once the pipeline (or capacity test) finishes, the database is aggregated and automatically exported to the Flask Web Dashboard. You can explore the classified audio files and confidence scores at:

- `http://dashboard-ucabmjc.comp0235.condenser.arc.ucl.ac.uk/`

Monitoring Cluster Health:
Real-time metrics, including model load times, inference speeds, and cumulative processing counts across all worker nodes, are tracked via Prometheus and can be visualized at:

- `http://prometheus-ucabmjc.comp0235.condenser.arc.ucl.ac.uk/`