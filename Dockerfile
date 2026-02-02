# Base image
FROM ubuntu:22.04

# Set environment variables for non-interactive install
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/shadowshield/.venv/bin:$PATH"

# Set workdir early to reduce context switches
WORKDIR /opt/shadowshield

# Install system dependencies
RUN apt-get update && \
apt-get install -y \
python3 python3-pip python3-venv iptables ipset \
suricata curl vim git build-essential autoconf automake && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

# Build and install Portspoof
# Build and install Portspoof
RUN git clone https://github.com/drk1wi/portspoof.git /opt/portspoof && \
    cd /opt/portspoof && autoreconf -i && ./configure && make && make install && \
    wget -O /opt/portspoof/portspoof.conf https://raw.githubusercontent.com/drk1wi/portspoof/master/tools/portspoof.conf && \
    wget -O /opt/portspoof/services https://raw.githubusercontent.com/drk1wi/portspoof/master/tools/portspoof_signatures


# Copy your source code
COPY . /opt/shadowshield

# Set up Python virtual environment and install dependencies
RUN python3 -m venv .venv && \
pip install --upgrade pip && \
pip install -r requirements.txt

# Make scripts executable
RUN chmod +x docker-entrypoint.sh \
scripts/configure_cowrie.sh

# Run configuration scripts
RUN scripts/configure_cowrie.sh && \
python scripts/configure_suricata.py && \
python scripts/patch_suricata_config.py

# Entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
