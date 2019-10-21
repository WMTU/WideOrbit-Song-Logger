# WideOrbit Song Logger -- WOAFR Widget

Current version: 2.1

Java widget for logging songs to the webapp backend from WideOrbit Automation for Radio

Required Java libraries:

- [Apache Commons Lang3 3.9](http://mirror.cc.columbia.edu/pub/software/apache//commons/lang/binaries/commons-lang3-3.9-bin.zip)
- [Log4J 2.12.1](https://www.apache.org/dyn/closer.lua/logging/log4j/2.12.1/apache-log4j-2.12.1-bin.zip)

Widget package structure: (.zip file)

```text
+---classes
|   +---fm
|       +---wmtu
|           +---resources
|           |   \---LoggingWidget.png
|           |   \---messages.properties
|           \---LoggingWidget.class (make sure to include all subclass files here too)
+---lib
|   /---commons-lang3-3.9.jar
|   /---log4j-1.2-api-2.12.1.jar
|   /---log4j-core-2.12.1.jar
+---resources
|   /---config.properties
/---plugin.xml
```

Compiling:

```text
javac -cp .:lib/commons-lang3-3.9.jar:lib/log4j-1.2-api-2.12.1.jar:lib/log4j-api-2.12.1.jar:lib/log4j-core-2.12.1.jar:log/ras-core-api.jar LoggingWidget.java
```

## LoggingWidget.java

The java source of the widget.

## plugin.xml

An xml file describing the widget package.

## resources/config.properties.example

Example database configuration.

## classes/fm/wmtu/resources/LoggingWidget.png

An icon for the widget in the WO Automation for Radio interface.
