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
      coil_elements:
        expecting: HEA;HEP
```

If you want to display a custom message when an error is detected, you can 
add the optional `message` key and a corresponding value

```yaml
- selector:
    series_description: localizer_32ch_uncombined
    image_type: [ORIGINAL, PRIMARY, M, ND]
  plugins:
    params:
      coil_elements:
        expecting: HEA;HEP
        message: make sure the head coil is fully seated
```

You can also check if the standard deviation of every scan frame is less than 
a chosen value using the `std` plugin. This can identify noisy receive coils

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

If there is no exact match for an expected value, you can use a regular 
expression. For example, if you want your uncombined localizer `selector` 
to match both Siemens Skyra and Prisma scanners, you could do something 
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
      num_files:
        expecting: 96
      coil_elements:
        expecting: HEA;HEP
        message: make sure the head coil is fully seated
    std:
      lt:
        expecting: 0.7
- selector:
    series_description: ABCD_fMRI_rest_Skyra
  plugins:
    params:
      patient_position:
        expecting: HFS
      num_slices:
        expecting: 60
      num_volumes:
        expecting: 383
      pixel_spacing:
        expecting: [2.4, 2.4]
      base_resolution:
        expecting: [90, 0, 0, 90]
      percent_phase_field_of_view:
        expecting: 100
      slice_thickness:
        expecting: 2.4
      echo_time:
        expecting: 35
      repetition_time:
        expecting: 890
      coil_elements:
        expecting: HEA;HEP
      flip_angle:
        expecting: 52
      prescan_norm:
        expecting: Off
      bandwidth:
        expecting: 2220
      pe_direction:
        expecting: COL
      orientation_string:
        expecting: regex(Tra>.*)
    volreg:
      params: null
```

## Available plugins
You may choose any number of plugins to run on incoming data

1. `params` - Validate DICOM headers 
2. `volreg` - Plot 4-D scan (e.g., BOLD) motion
3. `std` - Compute the standard deviation of pixel data

