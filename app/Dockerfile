FROM python:3.10

RUN apt-get update && apt-get install -y --no-install-recommends wget \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip3 install poetry

# Setting the working directory
WORKDIR /app

COPY pyproject.toml ./
#Install the dependencies
RUN poetry install --no-root

# Copying our application into the container
COPY spamoverflow spamoverflow

# Get the version of spamhammer that matches the architecture of the container
RUN dpkg --print-architecture | grep -q "amd64" && export SPAMHAMMER_ARCH="amd64" || export SPAMHAMMER_ARCH="arm64" && wget https://github.com/CSSE6400/SpamHammer/releases/download/v1.0.0/spamhammer-v1.0.0-linux-${SPAMHAMMER_ARCH} -O spamoverflow/spamhammer && chmod +x spamoverflow/spamhammer

# Running our application
CMD ["poetry", "run", "flask", "--app", "spamoverflow", "run", "--host", "0.0.0.0", "--port", "8080"]