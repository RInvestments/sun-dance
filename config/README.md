# How to write process-config files
These are the process-config files. Intended to be used with `sundance_multi.py` script.
This script essentially is a wrapper for the underlying cli.
Documentation for writing it is as follows. 

Recently, I am moving towards `sundance_multi.py` (from sundance.py). It is nearly the same format 
as the earlier file. But with this you are able to specify multiple type of processes
and joins along with repeat durations. The documentation for consolidated format is as follows: 

Just two of the config files are actually relavant:

- retrive-parse-insert.config.xml
- retrive-parse-insert-recent-quotes.config.xml

## Example / Documentation
```
  <xml>
    <global>
    <store_dir>equities_db/data_X/</store_dir>
    <list_db>equities_db/lists/</list_db>
    <verbosity>0</verbosity>
    </global>

    <execution>
      <line>retriver_group</line>
      <line>parser_group</line>
      .
      .
      <line></line>
    </execution>

    <group id="retriver_group" >
      <process></process>
      <process></process>
      .
      .
      <process></process>
    <group>

    <group id="parser_group" >
      <process></process>
      <process></process>
      .
      .
      <process></process>
    <group>

    .
    .
    .
  </xml>


```



## Sequence in which, these configs are expected to be run (old way - deprecated)
- python sundance.py -f retrive_wsj.config.xml
- python sundance.py -f parse_wsj.config.xml
- python sundance.py -f delete_raw_wsj.config.xml
- python sundance.py -f insert_wsj.config.xml
- python sundance.py -f retrive_recent_quotes.config.xml
- python sundance.py -f insert_quotes.config.xml
