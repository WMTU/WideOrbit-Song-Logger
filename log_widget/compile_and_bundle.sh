#!/bin/bash

# this is really quick and dirty and basically assumes everything it needs to compile is already there

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

rm ./classes/fm/wmtu/*.class

javac -cp .:lib/commons-text-1.9.jar:lib/commons-lang3-3.11.jar:lib/log4j-1.2-api-2.12.1.jar:lib/log4j-api-2.12.1.jar:lib/log4j-core-2.12.1.jar:lib/ras-core-api.jar LoggingWidget.java

mv *.class ./classes/fm/wmtu/

if [ -f LoggingWidget.zip ]; then 
    rm LoggingWidget.zip 
fi

zip -rq LoggingWidget.zip classes lib resources plugin.xml

exit 0