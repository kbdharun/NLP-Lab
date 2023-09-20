# Use the official Ubuntu image as the base image
FROM ubuntu:latest

# Set environment variables to non-interactive mode during installation
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install required packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

# Install NLTK and other required Python packages
RUN pip3 install nltk

# Download NLTK data (all packages)
RUN python3 -c "import nltk; nltk.download('all')"

# Set up a non-root user to run VSCode Dev Container
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Switch to the non-root user
USER $USERNAME

# Set the working directory
WORKDIR /workspace

# Create a volume for VSCode to mount the project
VOLUME ["/workspace"]

# Expose any necessary ports
# EXPOSE <PORT>

# Add any additional setup or commands here

# Specify the entry point
# CMD [ "python3", "your_script.py" ]
