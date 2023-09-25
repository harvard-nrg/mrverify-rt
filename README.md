Scan Buddy
============
Traditional MRI quality control pipelines take place _after_ the MRI has 
been captured and the participant has gone home. Scan Buddy is a DICOM 
receiver that you can place next to the scanner console that will ingest 
data in realtime and alert you to potential acquisition errors such as 
noisy data, incorrectly connected equipment, and excessive head motion.

## Table of contents
1. [Hardware requirements](#hardware-requirements)
2. [Installation](#installation)
3. [Running](#running-scan-buddy)
4. [Running as a container](#running-as-a-container)
5. [Configuration file](#configuation-file)
   1. [defining selectors](#defining-selectors)
   2. [defining plugins](#defining-plugins)
6. [Plugins](#plugins)
   1. [params](#params)
   2. [std](#std)
   3. [volreg](#volreg)
   4. [custom messages](#custom-messages)
   5. [regular expression matching](#regular-expression-matching)

## Hardware requirements
Scan Buddy is a simple command line tool that runs on modest hardware. 
Even something as small as a Raspberry Pi 4 with 8 GB of RAM would do.

## Installation
Scan Buddy is written in Python and depends on
[dcm2niix](https://github.com/rordenlab/dcm2niix) and a few tools from 
[AFNI](https://github.com/afni/afni) (because they're really fast).

You can install everything on your own, or use 
[one of the provided containers](https://github.com/harvard-nrg/scanbuddy/pkgs/container/scanbuddy)
which are available for linux/amd64 or linux/arm64.

## Running Scan Buddy
To run Scan Buddy, run the `start.py` command line tool with a custom 
[configuration file](#configuration-file)

```bash
start.py -c config.yaml
```

Refer to `start.py --help` for more options.

## Running as a container
A much easier way to run Scan Buddy is within a Singularity container, where 
all dependencies are pre-installed. First, you'll need to 
[install Singularity](https://docs.sylabs.io/guides/3.0/user-guide/installation.html).
Once you have Singularity installed, run the following command to download the 
container image

```bash
singularity build scanbuddy.sif docker://ghcr.io/harvard-nrg/scanbuddy:latest
```

Now you should be able to run the container with the following command

```bash
./scanbuddy.sif -c config.yaml
```

## Configuration file
At it's core, Scan Buddy works off of a configuration file. Here's how to 
create one.

### defining selectors 
Scan Buddy passes every incoming scan through a `selector` and in turn will 
run any defined `plugins` on a matching scan. For example, to target an uncombined 
localizer, you might use the following `selector`

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
```

This will select any scan that matches the expected `series_description` **AND** 
`image_type`. When Scan Buddy finds a match, it will proceed with running any 
configured [plugins](#plugins).

### defining plugins
For each scan, you're able to register plugins within the `plugins` section. 
For a description of available plugins, skip to 
[Available Plugins](#plugins).

## Plugins
Here are all plugins that exist out of the box.

### params
You can use the `params` plugin to check specific DICOM headers. For example, checking 
the `coil_elements` header for the string `HEA;HEP` can detect an improperly seated 
head coil

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
  plugins:
    params:
      coil_elements:
        expecting: HEA;HEP
```

### std
You can check whether or not the standard deviation of every frame is less than 
a particular value using the `std` plugin. This is useful for identifying especially 
noisy receive coils

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
  plugins:
    params:
      coil_elements:
        expecting: HEA;HEP
        message: make sure the head coil is fully seated
    std:
      lt:
        expecting: 0.7
```

### volreg
You can have Scan Buddy run a fast volume registration on a BOLD scan using
the `volreg` plugin

> **Note**
> Since `volreg` accepts no paramters, you would use `volreg: null`

```yaml
- selector:
    series_description: ABCD_fMRI_rest_Skyra
  plugins:
    volreg: null
```

### custom messages
When there's an error detected, Scan Buddy will print a message like so

```bash
PatientName::localizer_32ch_uncombined::2 - coil_elements - expected "HEA;HEP" but found "HEA"
```

Admittedly, these messages can be a little cryptic. If you want to display a 
custom message when a particular type of error is detected, you can add a 
`message` element

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
  plugins:
    params:
      coil_elements:
        expecting: HEA;HEP
        message:  make sure the head coil is fully seated
```

### regular expression matching
If there is no exact match for an expected value within a `selector` or a 
`plugin`, you can use a regular expression. 

For example, if you want your uncombined localizer `selector` to match both 
Siemens Skyra and Prisma scanners, you would use something like this

```yaml
- selector:
    series_description: regex(localizer_(Skyra_)?32ch_uncombined)
    image_type: [ORIGINAL, PRIMARY, M, ND]
```
