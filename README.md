Scan Buddy
============
Scan Buddy is a simple DICOM C-STORE receiver that will process scans as they 
arrive. The primary use case is detecting MRI acquisition errors.

## Running Scan Buddy
To run Scan Buddy, run the `start.py` command line tool with a 
properly formatted [configuration file](#configuration-file)

```bash
start.py -c config.yaml
```

Refer to `start.py --help` for more options.

## Singularity
The easiest way to run Scan Buddy is within a Singularity container. First, run 
the following command to download the container image

```bash
singularity build scanbuddy.sif docker://ghcr.io/harvard-nrg/scanbuddy:latest
```

Now, you can run the container with the following command

```bash
./scanbuddy.sif -c config.yaml
```

## Configuration file
At it's core, Scan Buddy works off of a configuration file that _you_ define. 

### selectors 
Scan Buddy passes every incoming scan through a `selector` and will run any 
defined `plugins` on those scans. For example, to target an uncombined 
localizer, you might use the following `selector`

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
```

This will select any scan that matches the expected `series_description` **AND** 
`image_type`. When an incoming scan is a correct match, Scan Buddy will proceed 
with running any configured [plugins](#plugins).

### plugins
For each scan, you're able to register plugins within the `plugins` section. 
For example, you can use the `params` plugin to check specific DICOM headers. 
Checking the`coil_elements` DICOM header for the string `HEA;HEP` can detect 
an improperly seated head coil

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
  plugins:
    params:
      coil_elements: HEA;HEP
```

You can also check if the standard deviation of every scan frame is less than 
a chosen value using the `std` plugin. This can identify noisy receive coils

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
  plugins:
    params:
      coil_elements: HEA;HEP
    std:
      lt: 0.7
```

If there is no exact match for an expected value, you can use a regular 
expression. For example, if you want your uncombined localizer `selector` 
to match both Siemens Skyra and Prisma scanners, you might do something 
like this

```yaml
- selector:
    series_description: regex(localizer_(Skyra_)?32ch_uncombined)
    image_type: [ORIGINAL, PRIMARY, M, ND]
```

Here's a slightly more fleshed out configuration file

```yaml
- selector:
    series_description: regex(localizer_(Skyra_)?32ch_uncombined)
    image_type: [ORIGINAL, PRIMARY, M, ND]
  plugins:
    params:
      num_files: 96
      coil_elements: HEA;HEP
    std:
      lt: 0.7
- selector:
    series_description: ABCD_fMRI_rest_Skyra
  plugins:
    params:
      patient_position: HFS
      num_slices: 60
      num_volumes: 383
      pixel_spacing: [2.4, 2.4]
      base_resolution: [90, 0, 0, 90]
      percent_phase_field_of_view: 100
      slice_thickness: 2.4
      echo_time: 35
      repetition_time: 890
      coil_elements: HEA;HEP
      flip_angle: 52
      prescan_norm: Off
      bandwidth: 2220
      pe_direction: COL
      orientation_string: regex(Tra>.*)
    volreg:
      params: null
```

## Available plugins
You may choose any number of plugins to run on incoming data

1. `params` - Validate DICOM headers 
2. `volreg` - Plot 4-D scan (e.g., BOLD) motion
3. `std` - Compute the standard deviation of pixel data

