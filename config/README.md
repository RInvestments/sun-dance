# How to write process-config files
These are the process-config files. Intended to be used with sundance.py script.
This script essentially is a wrapper for the underlying cli.
Documentation for writing it is as follows.

## Sequence in which, these configs are expected to be run
- python sundance.py -f retrive_wsj.config.xml
- python sundance.py -f parse_wsj.config.xml
- python sundance.py -f delete_raw_wsj.config.xml
- python sundance.py -f insert_wsj.config.xml
- python sundance.py -f retrive_recent_quotes.config.xml
- python sundance.py -f insert_quotes.config.xml


## Example / Documentation
```
<xml>
  <global>
    <!-- (required) directory where data is stored -->
    <store_dir>equities_db/test_db/</store_dir>

    <!-- (required) directory where stocks lists are stored -->
    <list_db>equities_db/lists/</list_db>

    <!-- verbosity (0 to 5). 0: Minimum display. 5: Maximum display.
    (optional). If not specified will be set to zero. Can be either be global
    or can be set individually for every process
    -->
    <verbosity>0</verbosity>

    <!-- Directory where the log files need to be put. (optional)
        if this is unspecified than store_dir is used, with file prefix as
        process[-1].type . This can only be set globally
    -->
    <log_dir>equities_db/test_db/</log_dir>
  </global>

  <!-- Specify Independent Processes. Each <process> ... </process>
       will be run as independent thread. Following are examples of different types of valid types
  -->


  <!-- Retriver -->
  <process>
    <type>retriver</type>
    <task>wsj</task>
    <exchange>amex,hk</exchange> <!-- this can be a comma separate list of supported exchanges -->
    <verbosity>1</verbosity>
  </process>


  <!-- Inserter -->
  <process>
    <type>parser</type>
    <task>wsj</task>
    <exchange>xnyse</exchange>
  </process>


  <!-- Inserter -->
  <process>
    <type>inserter</type>
    <exchange>xsse,xszse</exchange>
    <vebosity>2</verbosity>
  </process>


</xml>
```
