#!/bin/bash

# Exit on error
set -e

echo "Creating fresh transformers environment with Python 3.10..."
conda create -n transformers python=3.10 -y
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate transformers

echo "Installing PyTorch first to ensure numpy compatibility..."
conda install pytorch=2.1.0 torchvision=0.16.0 -c pytorch -y

echo "Installing pandas and other data science packages..."
conda install -c conda-forge pandas=2.1.1 matplotlib=3.8.0 seaborn=0.13.0 scikit-learn=1.3.1 plotly=5.18.0 -y

echo "Installing transformers and related packages..."
pip install transformers==4.30.2 datasets==2.14.5 evaluate==0.4.0 accelerate==0.23.0 safetensors

echo "Environment setup complete! To use it, run: conda activate transformers"
echo "Current environment packages:"
conda list