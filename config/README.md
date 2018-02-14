# How to write process-config files
These are the process-config files. Intended to be used with `sundance_multi.py` script.
This script essentially is a wrapper for the underlying cli.
Documentation for writing it is as follows.

Recently, I am moving towards `sundance_multi.py` (from sundance.py). It is nearly the same format
as the earlier file. But with this you are able to specify multiple type of processes
and joins along with repeat durations. The documentation for consolidated format is described
in detail at the end of this document. You need to specify a) **global** variables,
b) **execution** which contains **lines** which actually specify execution group, c) **group**
which specify the **process** that need to run in parallel. See examples.


Just three of the config files are actually relavant:

- retrive-parse-insert.config.xml
- retrive-parse-insert-recent-quotes.config.xml
- retrive-parse-insert-15yr-quotes.config.xml

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
