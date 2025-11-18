#!/bin/bash

# Run all plotting scripts (plot1.py, plot2.py, plot3.py, plot4.py)
# This script should be executed from the FlowSign_graph directory

echo "Running plot1.py..."
python plot1.py

echo "Running plot2.py..."
python plot2.py

echo "Running plot3.py..."
python plot3.py

echo "Running plot4.py..."
python plot4.py

echo "All plots have been generated successfully!"
echo "Output files are saved in ../Graph/"

