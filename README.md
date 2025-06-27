Hackathon-type attempt at creating a simple frontend for playing around with pm4py.

Dummy dataset borrowed from the NHS E Process Mining Team 🙏

This would need some more work to make it more robust and modular if intended for any intensive use.

## Trying out online

The app is hosted at ``

> [!CAUTION]
> Do not upload any real data when using the hosted version.

## Running Locally

To run the app, clone the repository to your machine.

From the root of the repository folder, run `



# Plans and possible extensions

- add petri nets and other pm4py plots
- separate out cross-tab and per-tab controls
- stlite version (hosted, but runs locally on user's device using pyodide - would like to confirm more about exact mode of action and what does/doesn't leave users browser in testing, but my understanding is fundamentally this would be a secure option)
- add 'copy/view generated code' feature to allow copying out of the code that is generating the plot (from start to finish? Or separate preprocessing/visualisation?)
- add download button for plots
