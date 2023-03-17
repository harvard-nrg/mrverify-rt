FROM rockylinux:8

# install useful things
RUN dnf install -y git vim

# install some things
RUN dnf install -y python3 python3-devel

# set python to python3
RUN alternatives --set python /usr/bin/python3

# create a home directory for templateflow and mriqc cache
RUN mkdir -p /home/scanbuddy
ENV HOME=/home/scanbuddy

# install afni
ARG AFNI_PREFIX="/sw/apps/afni"
ARG AFNI_URI="https://afni.nimh.nih.gov/pub/dist/bin/misc/@update.afni.binaries"
RUN dnf install -y epel-release
RUN dnf install -y curl tcsh python2-devel libpng15 motif
RUN mkdir -p "${AFNI_PREFIX}"
WORKDIR "${AFNI_PREFIX}"
RUN curl -O "${AFNI_URI}"
RUN tcsh @update.afni.binaries -package linux_centos_7_64 -do_extras -bindir "${AFNI_PREFIX}"

# install dcm2niix
ARG D2N_PREFIX="/sw/apps/dcm2niix"
ARG D2N_URI="https://github.com/rordenlab/dcm2niix/releases/download/v1.0.20200331/dcm2niix_lnx.zip"
RUN dnf install -y unzip
RUN mkdir -p "${D2N_PREFIX}"
RUN curl -sL "${D2N_URI}" -o "/tmp/dcm2niix_lnx.zip"
WORKDIR "${D2N_PREFIX}"
RUN unzip "/tmp/dcm2niix_lnx.zip"
RUN rm "/tmp/dcm2niix_lnx.zip"

# install scanbuddy
ARG BUDDY_PREFIX="/sw/apps/scanbuddy"
ARG BUDDY_VERSION="x.y.z"
RUN python3 -m venv "${BUDDY_PREFIX}"
RUN dnf install -y gcc zlib-devel libjpeg-devel python3-tkinter
RUN "${BUDDY_PREFIX}/bin/pip" install "git+https://ncfcode.rc.fas.harvard.edu/nrg/scanbuddy.git#egg=scanbuddy"

# afni environment
ENV PATH="${AFNI_PREFIX}:${PATH}"

# dcm2niix environment
ENV PATH="${D2N_PREFIX}:${PATH}"

ENTRYPOINT ["/sw/apps/scanbuddy/bin/start.py"]
