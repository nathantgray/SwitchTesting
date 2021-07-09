The purpose of this program is to reproduce an error when 
commanding GridLAB-D switches through HELICS.

### Error description:
It is only possible to open and close a single switch and only one time.
Once one switch is opened it is not possible to command any other switches except to close the opened switch.

### To run test:
* In one console run `python main.py`.
* In a second console navigate to gridlabd/tiny and run `gridlabd tiny_main.glm`

### Results:
To see results of switching, open gridlabd/tiny/output/gpr_SWT_status.csv
