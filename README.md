# PySpectrometer2
The Second Incarnation of the Spectrometer project!

PySpectrometer2 Les Wright 2022
https://www.youtube.com/leslaboratory
https://github.com/leswright1977

This project is a follow on from: https://github.com/leswright1977/PySpectrometer 

This is a more advanced, but more flexible version of the original program. Tk has been dropped as the GUI to allow fullscreen mode on Raspberry Pi systems and the interface is designed to fit 800*480 screens, which seem to be a common resolution for RPi LCD's, paving the way for the creation of a stand alone benchtop instrument.

Whats new:
Higher reolution (800px wide graph)
3 row pixel averaging of sensor data
Fullscreen option for the Spectrometer graph
3rd order polymonial fit of calibration data for accurate measurement.
Improved graph labelling
Labelled measurement cursors
Optional waterfall display for recording spectra changes over time.
Key Bindings for all operations

All old features have been kept, including peak hold, peak detect, Savitsky Golay filter, and the ability to save graphs as png and data as CSV.

For instructions please consult the readme!

Future work:
It is planned to add in GPIO support, to allow the use of buttons and knobs to control the Spectrometer.
