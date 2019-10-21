# WideOrbit Discrepancy Logger -- WOAFR Widget

Java widget for logging DNP events to the webapp backend from WideOrbit Automation for Radio

Required Java libraries:

- [Apache Commons Lang3 3.9](http://mirror.cc.columbia.edu/pub/software/apache//commons/lang/binaries/commons-lang3-3.9-bin.zip)

Widget package structure: (.zip file)

```text
+---classes
|   +---fm
|       +---wmtu
|           +---resources
|           |   \---LoggingWidget.png
|           |   \---messages.properties
|           \---DiscrepancyWidget.class (make sure to include all subclass files here too)
+---lib
|   /---commons-lang3-3.9.jar
+---resources
|   /---config.properties
/---plugin.xml
```

Compiling:

```text
javac -cp .:lib/commons-lang3-3.9.jar:lib/ras-core-api.jar DiscrepancyWidget.java
```

## DiscrepancyWidget.java

The java source of the widget.

## plugin.xml

An xml file describing the widget package.

## resources/config.properties.example

Example database configuration.

## classes/fm/wmtu/resources/LoggingWidget.png

An icon for the widget in the WO Automation for Radio interface.
