FROM ubuntu:22.04

# --- Install system deps & build portspoof
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv iptables ipset \
    suricata curl vim psmisc git build-essential autoconf automake && \
    apt-get clean && \
    git clone https://github.com/drk1wi/portspoof.git /opt/portspoof && \
    cd /opt/portspoof && autoreconf -i && ./configure && make && make install

# --- Set working directory
WORKDIR /opt/shadowshield

# --- Copy app source
COPY . /opt/shadowshield

# --- Create and activate Python virtualenv & install deps
RUN python3 -m venv .venv && \
    . .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# --- Copy and make scripts executable
RUN chmod +x docker-entrypoint.sh \
    scripts/configure_cowrie.sh

# --- Run config scripts with venv activated
RUN . .venv/bin/activate && \
    scripts/configure_cowrie.sh && \
    python scripts/configure_suricata.py && \
    python scripts/patch_suricata_config.py

# --- Entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]
