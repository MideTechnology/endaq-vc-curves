Installation
------------
From the command line with your preferred Python install in the system path (virtualenv, system install, colab notebook, etc.), run

.. code-block:: sh
    
    python -m pip install git+https://github.com/MideTechnology/endaq-vc-curves.git

If you want to utilize the HTML plotting functions of the library, you should also similarly install `Plotly <https://plotly.com/>`_ via

.. code-block:: sh
    
    python -m pip install plotly

Usage
-----

The basic usage of this library should look something like this:

.. code-block:: python
    
    import bsvp

    # Get filenames
    filenames = [...]  # gather filenames via built-in `glob.glob`, colab's `google.colab.files.upload()`, or some other method

    # Calculate data
    calc_output = (
        bsvp.GetDataBuilder(accel_highpass_cutoff=1)
        .add_vc_curves(init_freq=1, bins_per_octave=3)
        .aggregate(filenames)
    )

    # Output calculations
    calc_output.to_csv_folder(folder_path="path/to/csvfiles")
    calc_output.to_html_plots(folder_path="path/to/plots")

For more information on what this library can do and how to use it, see the example jupyter notebook in this repo, and use the Python function `help()` to inspect the class/function documentation in this codebase.
