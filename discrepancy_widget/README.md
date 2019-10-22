# WideOrbit Discrepancy Logger -- WOAFR Widget

Java widget for logging DNP events to the webapp backend from WideOrbit Automation for Radio

Required Java libraries:

- [Apache Commons Lang 3.9](https://commons.apache.org/proper/commons-lang/download_lang.cgi)
- [Apache Commons Text 1.8](https://commons.apache.org/proper/commons-text/download_text.cgi)

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
|   /---commons-text-1.8.jar
+---resources
|   /---config.properties
/---plugin.xml
```

Compiling:

```text
javac -cp .:lib/commons-text-1.8.jar:lib/commons-lang3-3.9.jar:lib/ras-core-api.jar DiscrepancyWidget.java
```

## DiscrepancyWidget.java

The java source of the widget.

## plugin.xml

An xml file describing the widget package.

## resources/config.properties.example

Example database configuration.

## classes/fm/wmtu/resources/LoggingWidget.png

An icon for the widget in the WO Automation for Radio interface.
