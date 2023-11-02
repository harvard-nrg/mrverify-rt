Scan Buddy
============

<img width="400" alt="volreg" src="https://github.com/harvard-nrg/scanbuddy/assets/1966482/57907018-022c-4eac-96b7-47ee2e7e4b94">
<img width="400" alt="warning" src="https://github.com/harvard-nrg/scanbuddy/assets/1966482/1231d39c-3d59-4304-8f18-c666730c101a">

Scan Buddy is a lightweight configurable application that will ingest MRI data (over DICOM) 
and alert the user in realtime to common acquisition errors such as noisy data, incorrectly 
connected equipment, and excessive head motion.

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
Scan Buddy is a simple command line tool that will run on modest hardware. Even 
the user interface is entirely [terminal based](https://textual.textualize.io/).
Something as small as a Raspberry Pi 4 with 8 GB of RAM would suffice.

## Installation
Scan Buddy is written in Python and only one plugin `volreg` depends on the 
external command line tools
[`dcm2niix`](https://github.com/rordenlab/dcm2niix)
and [3dvolreg from
AFNI](https://github.com/afni/afni)
(because these tools are fast).

You can certainly install everything on your own, or you can use 
[one of the provided containers](https://github.com/harvard-nrg/scanbuddy/pkgs/container/scanbuddy)
available for `linux/amd64` or `linux/arm64`.

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
At its core, Scan Buddy works off of a configuration file. Below you will find 
a quick walkthrough.

### defining selectors 
Every scan received by Scan Buddy is passed through a `selector` which will 
in turn run any defined `plugins` on that scan. To target an uncombined 
localizer, you would use the following `selector`

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
```

This will match any scan with that exact `series_description` **AND** 
`image_type`. When Scan Buddy finds a match, it will proceed with running any 
configured [plugins](#plugins).

### defining plugins
For each scan, you can register plugins within the `plugins` section. For a 
description of all available plugins, jump to [Available Plugins](#plugins).

## Plugins
Here are all available plugins.

### params
You can use the `params` plugin to validate DICOM headers. For example, checking 
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
You can use the `std` plugin to check whether or not the standard deviation of every 
image in a scan is less than a particular value. This is a useful plugin to run on 
an uncombined localizer to identify noisy receive coils

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
  plugins:
    params:
      coil_elements:
        expecting: HEA;HEP
    std:
      lt:
        expecting: 0.7
```

### volreg
You can use the `volreg` plugin to have Scan Buddy run a quick volume registration 
on a functional (4-D) scan

```yaml
- selector:
    series_description: ABCD_fMRI_rest_Skyra
  plugins:
    volreg:
      overview: true
```

Setting `overview: true` will display a small summary of displacements between 
successive timepoints. This can be useful to see if there were any sudden head 
movements.

### custom messages
When there's an error detected, Scan Buddy will print a message to the screen

```bash
PatientName, scan 2, localizer_32ch_uncombined - coil_elements - expected "HEA;HEP" but found "HEA"
```

While this message is indeed true to the error that was detected, these messages can 
be a little cryptic and they offer no guidance on how to _correct_ the error. To 
display a more detailed error message, you can use the `message` element

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
  plugins:
    params:
      coil_elements:
        expecting: HEA;HEP
        message:  |
            Detected an issue with head coil elements.

            1. Check head coil connection for debris or other obstructions.
            2. Reconnect head coil securely.
            3. Ensure that anterior and posterior coil elements are present.

            Call 867-5309 for further assistance.
```

### Blue screen of death
For any type of error, you can have Scan Buddy display a scary looking red 
screen that must be manually dismissed. This option is named `bsod` as it 
is similar in spirit to the infamous 
[Blue Screen of Death](#https://en.wikipedia.org/wiki/Blue_screen_of_death)

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
  plugins:
    params:
      coil_elements:
        expecting: HEA;HEP
        message:  |
            Detected an issue with head coil elements.

            1. Check head coil connection for debris or other obstructions.
            2. Reconnect head coil securely.
            3. Ensure that anterior and posterior coil elements are present.

            Call 867-5309 for further assistance.
        bsod: true
```
 
This screen is intended to immediately capture the user's attention.

### regular expression matching
Sometimes there is no exact match for an expected value within a `selector` 
or the value a plugin is `expecting`. In these cases, you can use a regular 
expression. 

For example, if you want your uncombined localizer `selector` to match both 
Siemens Skyra and Prisma scanners, you would do something like this

```yaml
- selector:
    series_description: regex(localizer_(Skyra_)?32ch_uncombined)
    image_type: [ORIGINAL, PRIMARY, M, ND]
```

