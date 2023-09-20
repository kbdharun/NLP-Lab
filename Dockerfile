# Use the latest Ubuntu image as the base image
FROM ubuntu:latest

# Update and upgrade packages
RUN apt-get update && apt-get upgrade -y

# Install Python, pip, git, and Jupyter Notebook
RUN apt-get install -y python3 python3-pip git
RUN pip3 install notebook

# Install NLTK and other dependencies
RUN pip3 install nltk

# Create a directory for NLTK data and download 'all'
RUN python3 -m nltk.downloader all

# Set the working directory
WORKDIR /app

# Command to run when the container starts
CMD ["/bin/bash"]
